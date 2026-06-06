{
  nixConfig = {
    bash-prompt-prefix = "(proj) ";
  };

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
    python38-nixpkgs.url = "github:nixos/nixpkgs/7592790b9e02f7f99ddcb1bd33fd44ff8df6a9a7";
  };

  outputs = { self, nixpkgs, flake-utils, python38-nixpkgs, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };

      python38-pkgs = import python38-nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };

      lib = pkgs.lib;

      packages = rec {
        proj = pkgs.python3Packages.callPackage ./pkgs/proj {
          inherit pytest-skip-slow;
          inherit bencher-cli;
          inherit ff-clang-format;
          inherit rapidcheckFull;
          inherit doctest;
          inherit libassert;

          # for perf the kernel version doesn't matter as it's entirely in perl
          # see https://discourse.nixos.org/t/which-perf-package/22399
          perf = pkgs.linuxPackages_latest.perf;
        };
        bencher-cli = pkgs.callPackage ./pkgs/bencher.nix { };
        ff-clang-format = pkgs.callPackage ./pkgs/ff-clang-format.nix { };
        doctest = pkgs.callPackage ./pkgs/doctest { };
        pytest-skip-slow = pkgs.python3Packages.callPackage ./pkgs/pytest-skip-slow.nix { };
        proj-nvim = pkgs.callPackage ./pkgs/proj-nvim.nix { inherit proj; };
        libdwarf-lite = pkgs.callPackage ./pkgs/libdwarf-lite.nix { };
        cpptrace = pkgs.callPackage ./pkgs/cpptrace.nix { inherit libdwarf-lite; };
        libassert = pkgs.callPackage ./pkgs/libassert.nix { inherit cpptrace; };

        rapidcheckFull = pkgs.symlinkJoin {
          name = "rapidcheckFull";
          paths = (with pkgs; [ rapidcheck.out rapidcheck.dev ]);
        };

        default = proj;
      };
    in
    rec {
      inherit packages;

      apps = {
        default = {
          type = "app";
          program = "${self.packages.${system}.proj}/bin/proj";
        };
      };

      devShells = {
        ci = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.proj ];
        };

        default = pkgs.mkShell {
          inputsFrom = [
            self.packages.${system}.proj
          ];

          buildInputs = builtins.concatLists [
            (with pkgs; [
              cmake
              ccache
              nlohmann_json
              fmt
              cmake
              gbenchmark
              lcov
              gdb
              doxygen
              ninja
              universal-ctags
            ])
            (with python38-pkgs.python38Packages; [
              pip
            ])
            (with pkgs.python3Packages; [
              pip
              ipython
              # ipdb
              mypy
              tox
              pytest-xdist
              nclib
            ])
            (with self.packages.${system}; [
              rapidcheckFull
              pytest-skip-slow
              doctest
              libassert
            ])
          ];
        };
      };
    }
  );
}
# vim: set tabstop=2 shiftwidth=2 expandtab:
