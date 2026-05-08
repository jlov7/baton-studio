module.exports = {
  hooks: {
    readPackage(pkg) {
      if (pkg.name === "next" && pkg.version === "15.5.15") {
        pkg.dependencies = {
          ...pkg.dependencies,
          postcss: "8.5.14",
        };
      }

      return pkg;
    },
  },
};
