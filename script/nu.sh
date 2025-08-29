git clone https://github.com/nushell/nushell.git && cd nushell
git checkout -b $COMMIT

# export RUSTFLAGS="-C opt-level=3 -C target-cpu=x86-64-v3"
# export _CL_="/arch:AVX2 /O2 /GL /fp:fast"
# export _LINK_="/LTCG /OPT:REF /OPT:ICF"
export RUSTFLAGS=" -C target-cpu=x86-64-v3"
export _CL_=" /arch:AVX2"


cargo fetch --locked --target x86_64-pc-windows-msvc
cargo build --release --frozen --workspace

mkdir ../release
cp target/release/*.exe ../release/
