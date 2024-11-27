{
  inputs = {

    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, flake-utils, nixpkgs }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells = rec {
          default = pkgs.mkShell {
            packages = with pkgs; [
              geckodriver
              firefox
              (python3.withPackages (python-pkgs:
                with python-pkgs; [
                  pandas
                  numpy
                  scipy
                  matplotlib
                  scikit-learn
                  ipython
                  kneed
                  bokeh
                  selenium
                  tqdm
                  rich
                ]))
              (rWrapper.override {
                packages = with rPackages; [
                  ggplot2
                  NMF
                  genefilter
                  rstudioapi
                  httpgd
                ];
              })

            ];
          };
        };
      });
}
