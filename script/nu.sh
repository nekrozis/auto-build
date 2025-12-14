git clone https://github.com/nushell/nushell.git && cd nushell
git checkout -b $COMMIT

# export RUSTFLAGS="-C opt-level=3 -C target-cpu=x86-64-v3"
# export _CL_="/arch:AVX2 /O2 /GL /fp:fast"
# export _LINK_="/LTCG /OPT:REF /OPT:ICF"
# export RUSTFLAGS=" -C target-cpu=x86-64-v3"
# export _CL_=" /arch:AVX2"

export CL="/fp:fast"
export _CL_="/arch:AVX2 /O2"
export RUSTFLAGS="-C target-cpu=x86-64-v3"

cat <<EOF >> ./Cargo.toml
[profile.makepkg]
inherits = "release"
opt-level = 3
debug = false
strip = "debuginfo"
debug-assertions = false
overflow-checks = false
lto = true
panic = 'unwind'
incremental = false
codegen-units = 1
rpath = false
EOF

rm -rf ./.cargo/ && ls -al

cargo fetch --locked --target x86_64-pc-windows-msvc
cargo build --profile makepkg --frozen

strip --strip-all target/makepkg/*.exe
mkdir ../release
cp target/makepkg/*.exe ../release/
