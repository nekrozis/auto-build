export CMAKE_PREFIX_PATH=$PWD/build/qt6/build/lib/cmake

pushd build

git clone https://github.com/Mahdi-zarei/nekoray.git 
pushd nekoray
git checkout $NEKORAY_VERSION

mkdir protoc
curl -L "https://github.com/protocolbuffers/protobuf/releases/download/${PROTOBUF_VERSION}/protoc-${PROTOBUF_VERSION#v}-win64.zip" -o protoc/protoc.zip
unzip protoc/protoc.zip
rm deps/bin/* -f
cp protoc/bin/protoc.exe deps/bin/

popd

mkdir -p nekoray/libs/deps
mv deps nekoray/libs/deps/built
ls -l nekoray/libs/deps/built
nekoray/libs/deps/built/bin/protoc.exe --version

mkdir nekoray/build
pushd nekoray/build

cmake -GNinja -DCMAKE_BUILD_TYPE=Release -DQT_VERSION_MAJOR=6 -DCMAKE_CXX_FLAGS="-static -DNDEBUG -s" ..
cmake --build . --parallel

popd
popd

ls -l build/nekoray/build
