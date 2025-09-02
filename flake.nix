{
  description = "Frontend + Docker Dev Env";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux"; 
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.docker
          pkgs.docker-compose
          pkgs.nodejs_20
          pkgs.nodePackages.npm
        ];

        shellHook = ''
          echo "Dev shell ready: Node, Docker, Docker-Compose available"
        '';
      };
    };
}
