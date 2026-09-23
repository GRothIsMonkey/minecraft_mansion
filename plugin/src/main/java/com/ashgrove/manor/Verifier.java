package com.ashgrove.manor;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import org.bukkit.Art;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.BlockFace;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.Entity;
import org.bukkit.entity.ItemFrame;
import org.bukkit.entity.Painting;
import org.bukkit.scheduler.BukkitRunnable;

import java.util.ArrayList;
import java.util.List;

/**
 * Compares the world with the finished design, block by block, over every block the build
 * writes (see tools/plugin_export.py for the encoding), then checks the paintings, the item
 * frame and the armor stands. Blocks the build does not write are your own terrain and are
 * not checked.
 */
final class Verifier extends BukkitRunnable {

    private static final BlockFace[] FACING = {BlockFace.SOUTH, BlockFace.WEST, BlockFace.NORTH, BlockFace.EAST};

    private final AshgroveManorPlugin plugin;
    private final World world;
    private final byte[] cells;
    private final CommandSender sender;
    private final int x1, y1, z1, nx, ny, nz;
    private int cell;
    private int checked, wrong, water, deadGrass;
    private final List<String> examples = new ArrayList<String>();

    Verifier(AshgroveManorPlugin plugin, World world, byte[] cells, CommandSender sender) {
        this.plugin = plugin;
        this.world = world;
        this.cells = cells;
        this.sender = sender;
        int[] b = plugin.box;
        x1 = b[0];
        y1 = b[1];
        z1 = b[2];
        nx = b[3] - b[0] + 1;
        ny = b[4] - b[1] + 1;
        nz = b[5] - b[2] + 1;
    }

    @Override
    public void run() {
        long t0 = System.nanoTime();
        int total = nx * ny * nz;
        while (cell < total && System.nanoTime() - t0 < 25000000L) {
            for (int k = 0; k < 2048 && cell < total; k++, cell++) {
                int flags = cells[2 * cell + 1] & 0xff;
                if ((flags & 0x80) == 0) {
                    continue;
                }
                int want = cells[2 * cell] & 0xff;
                int meta = flags & 15;
                int cls = (flags >> 4) & 7;
                int x = x1 + cell % nx;
                int z = z1 + (cell / nx) % nz;
                int y = y1 + cell / (nx * nz);
                int id = world.getBlockTypeIdAt(x, y, z);
                boolean ok;
                switch (cls) {
                    case 0: {
                        ok = id == want && (id == 0 || world.getBlockAt(x, y, z).getData() == meta);
                        break;
                    }
                    case 1:
                        ok = id == want;
                        break;
                    case 2:
                        ok = id == 2 || id == 3;
                        if (id == 3) {
                            deadGrass++;
                        }
                        break;
                    case 3:
                        ok = id == 0 || id == 8 || id == 9;
                        if (id == 8 || id == 9) {
                            water++;
                        }
                        break;
                    default:
                        ok = id == 8 || id == 9;
                }
                checked++;
                if (!ok) {
                    wrong++;
                    if (examples.size() < 12) {
                        Block blk = world.getBlockAt(x, y, z);
                        examples.add("  " + x + " " + y + " " + z + ": design " + name(want) + ":" + meta
                                + ", world " + name(id) + ":" + blk.getData());
                    }
                }
            }
        }
        if (cell >= total) {
            cancel();
            finish();
        }
    }

    private void finish() {
        List<String> report = new ArrayList<String>();
        int[] b = plugin.box;
        List<Painting> paintings = new ArrayList<Painting>();
        List<ItemFrame> frames = new ArrayList<ItemFrame>();
        List<ArmorStand> stands = new ArrayList<ArmorStand>();
        for (Entity e : world.getEntities()) {
            Location l = e.getLocation();
            if (l.getX() < b[0] - 1 || l.getX() > b[3] + 2 || l.getY() < b[1] - 1 || l.getY() > b[4] + 2
                    || l.getZ() < b[2] - 1 || l.getZ() > b[5] + 2) {
                continue;
            }
            if (e instanceof Painting) {
                paintings.add((Painting) e);
            } else if (e instanceof ItemFrame) {
                frames.add((ItemFrame) e);
            } else if (e instanceof ArmorStand) {
                stands.add((ArmorStand) e);
            }
        }
        int wantP = 0, okP = 0, wantF = 0, okF = 0, wantS = 0, okS = 0;
        for (JsonElement el : plugin.expectedEntities()) {
            JsonObject o = el.getAsJsonObject();
            String type = o.get("type").getAsString();
            if (type.equals("Painting")) {
                wantP++;
                Art art = Art.getByName(o.get("motive").getAsString());
                BlockFace f = FACING[o.get("facing").getAsInt()];
                for (Painting p : paintings) {
                    if (p.getArt() == art && p.getFacing() == f && near(p.getLocation(), o, 1.6)) {
                        okP++;
                        paintings.remove(p);
                        break;
                    }
                }
            } else if (type.equals("ItemFrame")) {
                wantF++;
                BlockFace f = FACING[o.get("facing").getAsInt()];
                for (ItemFrame fr : frames) {
                    if (fr.getFacing() == f && fr.getItem() != null && fr.getItem().getType() != Material.AIR
                            && near(fr.getLocation(), o, 1.1)) {
                        okF++;
                        frames.remove(fr);
                        break;
                    }
                }
            } else if (type.equals("ArmorStand")) {
                wantS++;
                JsonElement pos = o.get("pos");
                for (ArmorStand s : stands) {
                    Location l = s.getLocation();
                    double dy = l.getY() - pos.getAsJsonArray().get(1).getAsDouble();
                    if (Math.abs(l.getX() - pos.getAsJsonArray().get(0).getAsDouble()) < 0.3
                            && Math.abs(l.getZ() - pos.getAsJsonArray().get(2).getAsDouble()) < 0.3
                            && dy > -0.6 && dy < 0.1) {
                        okS++;
                        stands.remove(s);
                        break;
                    }
                }
            }
        }
        boolean allOk = wrong == 0 && okP == wantP && okF == wantF && okS == wantS;
        String summary = String.format("%s: %,d of %,d built blocks match the design; paintings %d/%d, item frame %d/%d,"
                        + " armor stands %d/%d", allOk ? "OK" : "DIFFERENCES FOUND", checked - wrong, checked,
                okP, wantP, okF, wantF, okS, wantS);
        report.add(summary);
        if (water > 0 || deadGrass > 0) {
            report.add("  (game-made, harmless: " + water + " blocks of fountain water flowed out; " + deadGrass
                    + " grass blocks under walls turned to dirt)");
        }
        if (wrong > 0) {
            report.add("  First differences:");
            report.addAll(examples);
            report.add("  Run 'mansion verify' again after a moment; if they remain, 'mansion build' rebuilds.");
        }
        plugin.verifyDone(sender, report, summary);
    }

    private static boolean near(Location l, JsonObject o, double tol) {
        JsonElement blk = o.get("block");
        double bx = AshgroveManorPlugin.intAt(blk, 0) + 0.5;
        double by = AshgroveManorPlugin.intAt(blk, 1) + 0.5;
        double bz = AshgroveManorPlugin.intAt(blk, 2) + 0.5;
        return Math.abs(l.getX() - bx) < tol && Math.abs(l.getY() - by) < tol && Math.abs(l.getZ() - bz) < tol;
    }

    @SuppressWarnings("deprecation")
    private static String name(int id) {
        Material m = Material.getMaterial(id);
        return m == null ? String.valueOf(id) : m.name().toLowerCase();
    }
}
