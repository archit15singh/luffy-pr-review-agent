#!/usr/bin/env node
import { main } from "../src/cli.mjs";

main()
  .then((code) => process.exit(code ?? 0))
  .catch((err) => {
    console.error(err.message || err);
    process.exit(1);
  });
