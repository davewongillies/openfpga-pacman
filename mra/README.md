# ROM recipes (`.mra`)

These `.mra` files are the recipes a Pocket ROM updater (or the MiSTer
[`mra`](https://github.com/sebdel/mra-tools-c) tool) uses to assemble each
shipped game's `.rom` from your own MAME set.

| Recipe | MAME zip(s) | Output `.rom` |
|---|---|---|
| `Pac-Man.mra` | `pacman.zip` | `pacman.rom` |
| `Pac-Man (speedup).mra` | `pacmanf.zip` (+ `pacman.zip`) | `pacmanf.rom` |
| `Ms. Pac-Man.mra` | `mspacman.zip` | `mspacman.rom` |
| `Ms. Pac-Man (speedup).mra` | `mspacmnf.zip` (+ `mspacman.zip`) | `mspacmnf.rom` |

Each recipe's `index 0` is the flat image the core's `data_loader` streams to
bridge `0x00000000`. The per-game variant (mod) byte — `0` for Pac-Man, `5` for
Ms. Pac-Man — is **not** in the `.rom`; it is written by the per-game instance
JSON to bridge `0x50000000`.

Place the assembled `.rom` in `Assets/pacman/common/` on the SD card.

`tools/verify_mra.py` confirms every recipe assembles byte-for-byte to
`tools/build_roms.py`'s output.
