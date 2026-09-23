package com.ashgrove.manor;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Chunk;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.minecart.CommandMinecart;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.world.ChunkUnloadEvent;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.zip.GZIPInputStream;

/**
 * Builds the finished Ashgrove Manor (Claude base + Astra refurbishment, source commit 4be5b07).
 *
 * The plugin replays the exact list of vanilla 1.8 build commands that the tested 34-stage
 * console installer ran (3356 base + 1162 Astra, all with absolute coordinates), in the same
 * order, a few milliseconds per tick. Only the installer machinery (falling command blocks,
 * minecart piles, sky pad) is left out: it never was part of the mansion. The commands run
 * as a command-block minecart, the same kind of command sender the tested installer used.
 */
public final class AshgroveManorPlugin extends JavaPlugin implements Listener {

    static final String CART_NAME = "AshgroveInstaller";
    private static final String P = ChatColor.GOLD + "[Ashgrove] " + ChatColor.RESET;

    List<String> commands;
    int baseCommands;
    String baseItemSweep;
    int[] box;                       // x1 y1 z1 x2 y2 z2 (world, inclusive)
    int[] entrance;
    String commandsSha;
    JsonObject manifest;

    private File progressFile;
    private YamlConfiguration progress;
    private final Set<Long> pinned = new HashSet<Long>();
    private BuildTask buildTask;
    private BukkitTask verifyTask;
    private final Map<String, Long> pendingConfirm = new HashMap<String, Long>();

    // ------------------------------------------------------------------ lifecycle --
    @Override
    public void onEnable() {
        saveDefaultConfig();
        try {
            loadResources();
        } catch (Exception e) {
            getLogger().severe("The mansion data inside the JAR is damaged: " + e.getMessage());
            getServer().getPluginManager().disablePlugin(this);
            return;
        }
        progressFile = new File(getDataFolder(), "progress.yml");
        progress = YamlConfiguration.loadConfiguration(progressFile);
        getServer().getPluginManager().registerEvents(this, this);
        String state = progress.getString("state", "idle");
        getLogger().info("Ashgrove Manor ready: " + commands.size() + " build commands ("
                + baseCommands + " base + " + (commands.size() - baseCommands) + " Astra). Entrance "
                + entrance[0] + " " + entrance[1] + " " + entrance[2] + ", facing east.");
        if ("building".equals(state) || "paused".equals(state)) {
            getLogger().warning("A mansion build was interrupted at command " + progress.getInt("index")
                    + "/" + commands.size() + ". Type 'mansion resume' to build it again from the start"
                    + " (about two minutes; the result is exact).");
        } else if ("idle".equals(state)) {
            getLogger().info("Type 'mansion build' in the console to build the mansion.");
        }
    }

    @Override
    public void onDisable() {
        if (buildTask != null) {
            buildTask.stopAndSave("paused");
        }
        if (verifyTask != null) {
            verifyTask.cancel();
        }
    }

    private void loadResources() throws Exception {
        byte[] raw = readAll(getResource("ashgrove/commands.txt"));
        MessageDigest sha = MessageDigest.getInstance("SHA-256");
        commandsSha = hex(sha.digest(raw));
        manifest = new JsonParser().parse(new InputStreamReader(getResource("ashgrove/manifest.json"),
                StandardCharsets.UTF_8)).getAsJsonObject();
        if (!commandsSha.equals(manifest.get("commands_sha256").getAsString())) {
            throw new IOException("commands.txt checksum mismatch");
        }
        commands = new ArrayList<String>(4600);
        BufferedReader r = new BufferedReader(new InputStreamReader(
                new java.io.ByteArrayInputStream(raw), StandardCharsets.US_ASCII));
        String line;
        while ((line = r.readLine()) != null) {
            if (!line.isEmpty()) {
                commands.add(line);
            }
        }
        if (commands.size() != manifest.get("commands").getAsInt()) {
            throw new IOException("command count mismatch");
        }
        baseCommands = manifest.get("base_commands").getAsInt();
        baseItemSweep = manifest.get("base_item_sweep").getAsString();
        box = ints(manifest.getAsJsonArray("build_box"));
        entrance = ints(manifest.getAsJsonArray("entrance"));
    }

    byte[] expectedCells() throws IOException {
        byte[] data = readAll(new GZIPInputStream(getResource("ashgrove/expected.bin.gz")));
        try {
            String h = hex(MessageDigest.getInstance("SHA-256").digest(data));
            if (!h.equals(manifest.get("expected_sha256").getAsString())) {
                throw new IOException("expected.bin checksum mismatch");
            }
        } catch (java.security.NoSuchAlgorithmException e) {
            throw new IOException(e);
        }
        return data;
    }

    // ------------------------------------------------------------------- commands --
    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        String sub = args.length == 0 ? "help" : args[0].toLowerCase();
        if (sub.equals("build")) {
            if (buildTask != null) {
                sender.sendMessage(P + "A build is already running. Use 'mansion status'.");
                return true;
            }
            World w = targetWorld(sender);
            if (w == null) {
                return true;
            }
            String state = progress.getString("state", "idle");
            sender.sendMessage(P + ChatColor.RED + "BACK UP THE WORLD FIRST." + ChatColor.RESET
                    + " This clears and rebuilds X " + box[0] + ".." + box[3] + ", Y " + box[1] + ".." + box[4]
                    + ", Z " + box[2] + ".." + box[5] + " in world '" + w.getName() + "'.");
            if ("building".equals(state) || "paused".equals(state)) {
                sender.sendMessage(P + "An unfinished build exists; 'mansion confirm' (or 'mansion resume') builds it again from the start.");
            } else if ("complete".equals(state)) {
                sender.sendMessage(P + "The mansion was already built; building again replaces any changes"
                        + " made to it since.");
            }
            sender.sendMessage(P + "Type 'mansion confirm' within 60 seconds to start.");
            pendingConfirm.put(sender.getName(), System.currentTimeMillis());
            return true;
        }
        if (sub.equals("confirm")) {
            Long t = pendingConfirm.remove(sender.getName());
            if (t == null || System.currentTimeMillis() - t > 60000L) {
                sender.sendMessage(P + "Type 'mansion build' first.");
                return true;
            }
            if (buildTask != null) {
                sender.sendMessage(P + "A build is already running.");
                return true;
            }
            World w = targetWorld(sender);
            if (w != null) {
                startBuild(sender, w, 0, true);
            }
            return true;
        }
        if (sub.equals("resume")) {
            if (buildTask != null) {
                sender.sendMessage(P + "The build is already running.");
                return true;
            }
            String state = progress.getString("state", "idle");
            if (!"building".equals(state) && !"paused".equals(state)) {
                sender.sendMessage(P + "There is no unfinished build to resume (state: " + state + ").");
                return true;
            }
            World w = Bukkit.getWorld(progress.getString("world", ""));
            if (w == null) {
                sender.sendMessage(P + "The world '" + progress.getString("world") + "' is not loaded.");
                return true;
            }
            // Always start again from the first command. Every block the build writes is first set
            // by an unconditional /fill or /setblock before anything reads it, so a full run gives
            // exactly the design over any half-built state; continuing from a saved position could
            // replay commands against chunks that were (or were not) saved before a crash.
            msg(sender, "Resuming: the build starts again from the first command (about two minutes) so the"
                    + " result is exact whatever state the site was left in.");
            startBuild(sender, w, 0, false);
            return true;
        }
        if (sub.equals("pause") || sub.equals("stop")) {
            if (buildTask == null) {
                sender.sendMessage(P + "No build is running.");
            } else {
                buildTask.stopAndSave("paused");
                sender.sendMessage(P + "Paused at command " + progress.getInt("index") + "/" + commands.size()
                        + ". Type 'mansion resume' to build it again from the start.");
            }
            return true;
        }
        if (sub.equals("status")) {
            String state = buildTask != null ? "building" : progress.getString("state", "idle");
            int idx = buildTask != null ? buildTask.index : progress.getInt("index", 0);
            sender.sendMessage(P + "State: " + state + ", command " + idx + "/" + commands.size()
                    + " (" + (100 * idx / commands.size()) + "%).");
            if (progress.contains("last_verify")) {
                sender.sendMessage(P + "Last check: " + progress.getString("last_verify"));
            }
            return true;
        }
        if (sub.equals("verify")) {
            if (buildTask != null || verifyTask != null) {
                sender.sendMessage(P + "Please wait until the build or check that is running has finished.");
                return true;
            }
            World w = targetWorld(sender);
            if (w != null) {
                startVerify(sender, w);
            }
            return true;
        }
        sender.sendMessage(P + "Ashgrove Manor (final Claude + Astra design). Entrance " + entrance[0] + " "
                + entrance[1] + " " + entrance[2] + ", facing east.");
        sender.sendMessage(P + "mansion build   - start building (asks you to confirm)");
        sender.sendMessage(P + "mansion status  - show progress");
        sender.sendMessage(P + "mansion pause   - pause; mansion resume - build again from the start");
        sender.sendMessage(P + "mansion verify  - check the built mansion block by block");
        return true;
    }

    World targetWorld(CommandSender sender) {
        String name = getConfig().getString("world", "");
        World w = name == null || name.isEmpty() ? Bukkit.getWorlds().get(0) : Bukkit.getWorld(name);
        if (w == null) {
            sender.sendMessage(P + "World '" + name + "' is not loaded. Check config.yml.");
            return null;
        }
        if (w.getEnvironment() != World.Environment.NORMAL) {
            sender.sendMessage(P + "World '" + w.getName() + "' is not an overworld. Check config.yml.");
            return null;
        }
        return w;
    }

    // ----------------------------------------------------------------------- build --
    private void startBuild(CommandSender sender, World w, int from, boolean fresh) {
        if (fresh || !progress.contains("gamerule.logAdminCommands")) {
            progress.set("gamerule.logAdminCommands", w.getGameRuleValue("logAdminCommands"));
            progress.set("gamerule.commandBlockOutput", w.getGameRuleValue("commandBlockOutput"));
        }
        progress.set("world", w.getName());
        progress.set("commands_sha256", commandsSha);
        progress.set("index", from);
        progress.set("state", "building");
        progress.set("last_verify", null);
        saveProgress();
        // the build runs from a command-block minecart: quiet like the tested installer
        w.setGameRuleValue("logAdminCommands", "false");
        w.setGameRuleValue("commandBlockOutput", "false");
        pinChunks(w);
        removeStaleCarts(w);
        CommandMinecart cart = w.spawn(new Location(w, entrance[0] + 30.5, box[4] + 7, entrance[2] + 0.5),
                CommandMinecart.class);
        cart.setCustomName(CART_NAME);
        buildTask = new BuildTask(this, w, cart, sender, from);
        buildTask.runTaskTimer(this, 1L, 1L);
        msg(sender, "Building started" + (from > 0 ? " from command " + from : "") + ": " + commands.size()
                + " commands. Players may notice short pauses while the big walls go up.");
    }

    /** Called by the BuildTask when it stops (finished or paused). */
    void buildStopped(World w, String state, int index, CommandSender sender) {
        buildTask = null;
        progress.set("index", index);
        progress.set("state", state);
        restoreGamerules(w);
        saveProgress();
        removeStaleCarts(w);
        if ("complete".equals(state)) {
            msg(sender, ChatColor.GREEN + "Mansion construction complete." + ChatColor.RESET
                    + " Checking it block by block now...");
            startVerify(sender, w);
        } else {
            unpinChunks();
        }
    }

    void saveIndex(int index) {
        progress.set("index", index);
        saveProgress();
    }

    private void restoreGamerules(World w) {
        w.setGameRuleValue("logAdminCommands", progress.getString("gamerule.logAdminCommands", "true"));
        w.setGameRuleValue("commandBlockOutput", progress.getString("gamerule.commandBlockOutput", "true"));
    }

    // ---------------------------------------------------------------------- verify --
    private void startVerify(CommandSender sender, World w) {
        byte[] cells;
        try {
            cells = expectedCells();
        } catch (IOException e) {
            msg(sender, "Cannot check: " + e.getMessage());
            unpinChunks();
            return;
        }
        pinChunks(w);
        Verifier v = new Verifier(this, w, cells, sender);
        verifyTask = v.runTaskTimer(this, 5L, 1L);
    }

    void verifyDone(CommandSender sender, List<String> report, String summary) {
        verifyTask = null;
        unpinChunks();
        progress.set("last_verify", summary);
        saveProgress();
        for (String line : report) {
            msg(sender, line);
        }
    }

    // ---------------------------------------------------------------------- chunks --
    private void pinChunks(World w) {
        pinned.clear();
        int cx1 = (box[0] >> 4) - 2, cx2 = ((entrance[0] + 31) >> 4) + 2;
        int cz1 = (box[2] >> 4) - 2, cz2 = (box[5] >> 4) + 2;
        for (int cx = cx1; cx <= cx2; cx++) {
            for (int cz = cz1; cz <= cz2; cz++) {
                pinned.add(key(cx, cz));
                w.loadChunk(cx, cz, true);
            }
        }
    }

    private void unpinChunks() {
        pinned.clear();
    }

    @EventHandler
    public void onChunkUnload(ChunkUnloadEvent e) {
        if (!pinned.isEmpty()) {
            Chunk c = e.getChunk();
            if (pinned.contains(key(c.getX(), c.getZ()))) {
                e.setCancelled(true);
            }
        }
    }

    private void removeStaleCarts(World w) {
        for (CommandMinecart c : w.getEntitiesByClass(CommandMinecart.class)) {
            if (CART_NAME.equals(c.getCustomName())) {
                c.remove();
            }
        }
    }

    // --------------------------------------------------------------------- helpers --
    void msg(CommandSender sender, String text) {
        getLogger().info(ChatColor.stripColor(text));
        if (sender != null && !(sender instanceof org.bukkit.command.ConsoleCommandSender)) {
            try {
                sender.sendMessage(P + text);
            } catch (Exception ignored) {
                // the player may have left
            }
        }
    }

    private void saveProgress() {
        try {
            progress.save(progressFile);
        } catch (IOException e) {
            getLogger().warning("Could not save progress.yml: " + e.getMessage());
        }
    }

    private static long key(int cx, int cz) {
        return ((long) cx << 32) ^ (cz & 0xffffffffL);
    }

    private static int[] ints(JsonArray a) {
        int[] out = new int[a.size()];
        for (int i = 0; i < out.length; i++) {
            out[i] = a.get(i).getAsInt();
        }
        return out;
    }

    static byte[] readAll(InputStream in) throws IOException {
        if (in == null) {
            throw new IOException("resource missing from the JAR");
        }
        try {
            ByteArrayOutputStream out = new ByteArrayOutputStream(1 << 20);
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) {
                out.write(buf, 0, n);
            }
            return out.toByteArray();
        } finally {
            in.close();
        }
    }

    private static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) {
            sb.append(String.format("%02x", x & 0xff));
        }
        return sb.toString();
    }

    JsonArray expectedEntities() {
        return manifest.getAsJsonArray("entities");
    }

    static int intAt(JsonElement e, int i) {
        return e.getAsJsonArray().get(i).getAsInt();
    }
}
