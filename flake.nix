{
  description = "ESPHome device configurations - development shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "aarch64-darwin"
        "x86_64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f (
            import nixpkgs {
              inherit system;
              config.allowUnfreePredicate = pkg: builtins.elem (nixpkgs.lib.getName pkg) [ "1password-cli" ];
            }
          )
        );
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python313
            uv
            # Node from /nix/store lets pre-commit use it as the "system" node for
            # node hooks (markdownlint) instead of downloading one with nodeenv.
            nodejs_22
            markdownlint-cli
            pre-commit
            go-task
            gh
            _1password-cli
          ];

          env = {
            # Build the project venv (esphome etc.) on the nix Python rather than
            # letting uv download its own interpreter.
            UV_PYTHON = "${pkgs.python313}/bin/python3";
            UV_PYTHON_DOWNLOADS = "never";
          };

          # Python packages in the shell (pre-commit's deps) export their
          # site-packages via PYTHONPATH, which leaks into the 3.13 venv and
          # into uv's source builds. Nix-wrapped tools don't need it.
          shellHook = ''
            unset PYTHONPATH
          '';
        };
      });
    };
}
