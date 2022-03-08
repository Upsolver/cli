class Upsolver < Formula
  include Language::Python::Virtualenv

  desc "CLI for Upsolver with auto-completion and syntax highlighting"
  homepage "https://upsolver.com/"
  url "https://github.com/Upsolver/cli/releases/download/beta/cli-0.1.0.tar.gz"
  sha256 "96c440b89c364b661f66ef96d09858d5d88d9eb89b35af55eae712e4df3180b5"
  license "BSD-3-Clause"

  depends_on "poetry" => :build
  depends_on "python@3.10"

  resource "upsolver-cli" do
    url "https://github.com/Upsolver/cli/releases/download/beta/cli-0.1.0.tar.gz"
  end

  def install
    venv = virtualenv_create(libexec, "python3")

    resource("upsolver-cli").stage do
      system Formula["poetry"].opt_bin/"poetry", "build", "--format", "wheel", "--verbose", "--no-interaction"
      venv.pip_install Dir["dist/cli-*.whl"].first
    end

    venv.pip_install resources
    venv.pip_install_and_link buildpath
  end

  test do
    system bin/"upsolver", "--help"
  end
end
