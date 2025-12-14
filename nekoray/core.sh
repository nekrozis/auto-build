export CGO_ENABLED=0
export GOOS=windows
export GOARCH=amd64

mkdir build/core
DEST=$PWD/build/core

pushd build/nekoray/core/server
VERSION_SINGBOX=$(go list -m -f '{{.Version}}' github.com/sagernet/sing-box)
go build -v -o $DEST -trimpath -ldflags "-w -s -X 'github.com/sagernet/sing-box/constant.Version=${VERSION_SINGBOX}'" -tags "with_clash_api,with_gvisor,with_quic,with_wireguard,with_utls,with_ech,with_dhcp"
popd

ls -l build/core
