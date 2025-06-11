pushd build
git clone https://code.qt.io/qt/qt5.git qt6 -b $QT_VERSION
mkdir qt6/build
pushd qt6
./configure.bat -release -static -prefix ./build -static-runtime -submodules qtbase,qtimageformats,qtsvg,qttranslations -skip tests -skip examples -gui -widgets -init-submodules
cmake --build . --parallel
ninja install
popd
popd

ls -l build/qt6/build
