mkdir -p deploy/nekoray

pushd deploy/nekoray

curl -LO https://github.com/SagerNet/sing-geoip/releases/latest/download/geoip.db
curl -LO https://github.com/SagerNet/sing-geosite/releases/latest/download/geosite.db

cp ../../build/nekoray/build/nekoray.exe .
cp ../../build/core/nekobox_core.exe .
cp ../../build/nekoray/res/public/nekobox.png .

strip nekoray.exe
strip nekobox_core.exe

popd
