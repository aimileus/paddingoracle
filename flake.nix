{
  # To run: just install nix and type:
  # nix run .
  # in the current folder.
  description = "Padding oracle server for homework";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let pkgs = nixpkgs.legacyPackages.${system}; in
        {
          packages.default = pkgs.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            # Otherwise it compiles everything... takes ages
            preferWheels = true;
          };
        }
      );
}
