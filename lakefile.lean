import Lake
open Lake DSL

package "pirtm" where
  version := v!"0.1.0"

@[default_target]
lean_lib «PIRTM» where
  -- add library configuration options here
