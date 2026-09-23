package com.ashgrove.manor;

import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.minecart.CommandMinecart;
import org.bukkit.scheduler.BukkitRunnable;

/**
 * Runs the build commands, in order, a few milliseconds per tick.
 *
 * Every command is a vanilla 1.8 /fill, /setblock, /clone, /summon or /kill with absolute
 * coordinates. They are sent with the "minecraft:" prefix, so another plugin that registers a
 * command with the same name (for example /kill) can never take them over.
 */
final class BuildTask extends BukkitRunnable {

    private final AshgroveManorPlugin plugin;
    private final World world;
    private final CommandMinecart cart;
    private final CommandSender requester;
    private CommandSender sender;
    int index;
    private int lastReport = -1;
    private int ticks;
    private int errors;
    private boolean stopped;

    BuildTask(AshgroveManorPlugin plugin, World world, CommandMinecart cart, CommandSender requester, int from) {
        this.plugin = plugin;
        this.world = world;
        this.cart = cart;
        this.requester = requester;
        this.sender = cart;
        this.index = from;
    }

    @Override
    public void run() {
        if (stopped) {
            return;
        }
        long budget = Math.max(5, plugin.getConfig().getLong("tick-budget-ms", 30)) * 1000000L;
        long t0 = System.nanoTime();
        int n = plugin.commands.size();
        do {
            if (index >= n) {
                finish();
                return;
            }
            dispatch(plugin.commands.get(index));
            index++;
            if (index == plugin.baseCommands) {
                // the tested base installer removed dropped items in the site after its stages
                dispatch(plugin.baseItemSweep);
            }
        } while (System.nanoTime() - t0 < budget);
        ticks++;
        if (ticks % 20 == 0) {
            plugin.saveIndex(index);
        }
        int pct = 100 * index / n;
        if (pct / 10 != lastReport) {
            lastReport = pct / 10;
            plugin.msg(requester, "Building... " + index + "/" + n + " commands (" + pct + "%)");
        }
    }

    private void dispatch(String command) {
        String line = "minecraft:" + command;
        try {
            Bukkit.dispatchCommand(sender, line);
        } catch (RuntimeException e) {
            if (sender == cart) {
                // a server that cannot run vanilla commands from a minecart: use the console
                plugin.getLogger().warning("Minecart command sender refused (" + e + "); using the console. "
                        + "The console will show one line per build command.");
                sender = Bukkit.getConsoleSender();
                try {
                    Bukkit.dispatchCommand(sender, line);
                } catch (RuntimeException e2) {
                    fail(command, e2);
                }
            } else {
                fail(command, e);
            }
        }
    }

    private void fail(String command, RuntimeException e) {
        errors++;
        if (errors <= 10) {
            plugin.getLogger().warning("Command failed: " + command + " (" + e + ")");
        }
    }

    private void finish() {
        stopped = true;
        cancel();
        if (errors > 0) {
            plugin.msg(requester, errors + " commands raised errors; see the server log.");
        }
        plugin.buildStopped(world, "complete", index, requester);
    }

    /** Pause (or plugin disable): remember where we are. */
    void stopAndSave(String state) {
        if (stopped) {
            return;
        }
        stopped = true;
        cancel();
        plugin.buildStopped(world, state, index, requester);
    }
}
