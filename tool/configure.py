import os
import sys
import argparse

# Preset configurations

RUST_CONFIG = [
    ('enable', 'CONFIG_SYSTEM_TIME64'),
    ('enable', 'CONFIG_FS_LARGEFILE'),
    ('enable', 'CONFIG_DEV_URANDOM'),
    ('set-val', 'CONFIG_TLS_NELEM', '16'),
]

PRESETS = {
    'rust': RUST_CONFIG,
}


def run_command(cmd):
    ret = os.system(cmd)
    if ret != 0:
        print(f"Error executing command: {cmd}")
        sys.exit(1)


def is_nuttx_configured(nuttx_path):
    return os.path.exists(os.path.join(nuttx_path, '.config'))


def configure_nuttx(nuttx_path, board_config):
    os.chdir(nuttx_path)
    if is_nuttx_configured(nuttx_path):
        print("NuttX already configured, running distclean")
        run_command("make distclean")

    run_command(f"./tools/configure.sh {board_config}")


def apply_presets(nuttx_path, presets):
    if not is_nuttx_configured(nuttx_path):
        print("Error: .config file not found for applying presets")
        sys.exit(1)

    for preset in presets:
        if preset not in PRESETS:
            print(f"Warning: Unknown preset '{preset}', skipping")
            continue

        print(f"Applying {preset} preset:")
        for action, *params in PRESETS[preset]:
            if action == 'disable':
                cmd = f"kconfig-tweak --disable {params[0]}"
            elif action == 'enable':
                cmd = f"kconfig-tweak --enable {params[0]}"
            elif action == 'set-val':
                cmd = f"kconfig-tweak --set-val {params[0]} {params[1]}"
            else:
                print(f"Warning: Unknown action '{action}', skipping...")
                continue

            print(f"  {cmd}")
            run_command(cmd)

    # Run make olddefconfig to resolve dependencies
    os.chdir(nuttx_path)
    run_command("make olddefconfig")


def generate_clangd_config(nuttx_path):
    if not is_nuttx_configured(nuttx_path):
        print("Error: .config file not found for clangd configuration")
        sys.exit(1)

    config_path = os.path.join(nuttx_path, '.config')
    target = "thumbv7m"

    # Mapping of configuration to target
    config_to_target = {
        'CONFIG_ARCH_XTENSA': "xtensa",
        'CONFIG_ARCH_X86': "i686",
        'CONFIG_ARCH_X86_64': "x86_64",
        'CONFIG_ARCH_CORTEXM0': "thumbv6m",
        'CONFIG_ARCH_CORTEXM3': "thumbv7m",
        'CONFIG_ARCH_CORTEXM4': "thumbv7em",
        'CONFIG_ARCH_CORTEXM7': "thumbv7em",
        'CONFIG_ARCH_CORTEXM23': "thumbv8m.base",
        'CONFIG_ARCH_CORTEXM33': "thumbv8m.main",
        'CONFIG_ARCH_CORTEXM55': "thumbv8m.main",
        'CONFIG_ARCH_RV32': "riscv32",
        'CONFIG_ARCH_RV64': "riscv64",
    }

    # Read file to get target
    with open(config_path, 'r') as f:
        for line in f:
            for config, tgt in config_to_target.items():
                relconfig = f"{config}=y"
                if relconfig in line:
                    target = tgt
                    break
            else:
                continue
            break

    clangd_config = f"""
Index:
    StandardLibrary: No

InlayHints:
    Enabled: No

CompileFlags:
    Add: ["--target={target}"]
    Remove: ["-m*", "-f*"]
"""

    with open(os.path.join(nuttx_path, '..', '.clangd'), 'w') as f:
        f.write(clangd_config)


def main():
    parser = argparse.ArgumentParser(description='Configure and build NuttX')
    parser.add_argument(
        'board_config', help='Path to board configuration directory')
    parser.add_argument('--nuttx', '-n',
                        required=True,
                        help='Path to NuttX directory')
    parser.add_argument('--preset', '-p',
                        action='append',
                        choices=PRESETS.keys(),
                        help='Apply preset configuration (can be used multiple times)')
    args = parser.parse_args()

    # Convert paths to absolute
    NUTTX_PATH = os.path.abspath(args.nuttx)

    if not os.path.exists(NUTTX_PATH):
        print(f"NuttX path not found: {NUTTX_PATH}")
        sys.exit(1)

    print("Configuring NuttX...")
    configure_nuttx(NUTTX_PATH, args.board_config)

    if args.preset:
        print("Applying preset configurations...")
        apply_presets(NUTTX_PATH, args.preset)

    print("Generating .clangd configuration...")
    generate_clangd_config(NUTTX_PATH)

    print("Configuration completed successfully!")


if __name__ == "__main__":
    main()
