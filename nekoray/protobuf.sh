pushd build

mkdir deps
INSTALL_PREFIX=$PWD/deps
git clone --recurse-submodules -b $PROTOBUF_VERSION --depth 1 --shallow-submodules https://github.com/protocolbuffers/protobuf.git

mkdir protobuf/build
pushd protobuf/build

cmake .. -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -Dprotobuf_BUILD_TESTS=OFF \
    -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
    -Dprotobuf_BUILD_PROTOBUF_BINARIES=ON \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_FLAGS="-static"  \
    -DCMAKE_THREAD_LIBS_INIT="-l:libwinpthread.a"

cmake --build . --parallel
ninja install

popd
popd

ls -l build/deps/