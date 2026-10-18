# Clean-room policy

The J48 firmware and Wingman are written from public specifications, not from another programmer's source code.

- **What we use:** manufacturer datasheets, the JEDEC JESD3 fuse-map file standard, published programming specifications, and published descriptions of device programming algorithms. Every source used is listed in `docs/spec/`.
- **What we don't use:** source code from Afterburner or other GAL programmers. Their documentation may be read for behaviour (for example, which devices they support), but their code is not copied, translated or used as a reference while writing J48 code.
- **Compatibility:** Wingman reads and writes standard JED files. Matching a file format or interface is not the same as copying an implementation.
- **Process:** write or update the spec in `docs/spec/` first, citing sources; then implement from the spec.

The programming algorithms belong to the device manufacturers; implementations belong to their authors. This policy keeps the J48 free to choose its own license.
