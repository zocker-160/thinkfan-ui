maintainer="zocker_160 <zocker1600 at posteo dot net>"

name=thinkfan-ui
version=0.11.0
release=1
desc="A small gui app for Linux to control the fan speed and monitor temps on a ThinkPad"
homepage="https://github.com/zocker-160/thinkfan-ui"
#architectures=('x86_64')
architectures=('all')
licenses=('GPL-3.0-only')

provides=("thinkfan-ui")
#conflicts=('')
deps=('python3' 'python3-pyqt5' 'lm-sensors' 'policykit-1')
sources=("git+https://github.com/zocker-160/thinkfan-ui.git?~rev=$version")
#sources=("git+https://github.com/zocker-160/thinkfan-ui.git")
checksums=("SKIP")

scripts=(
  ["preinstall"]="preinstall.sh"
  ["preremove"]="preremove.sh"
)


package() {
  cd "$srcdir/$name"

  install -d -m755 src "$pkgdir/opt/$name"
  cp -r src/* "$pkgdir/opt/$name"

  install-binary linux_packaging/thinkfan-ui
  install-desktop linux_packaging/thinkfan-ui.desktop
  install-license LICENSE "$name/LICENSE"

  install -D -m644 linux_packaging/thinkfan-ui.svg -t "$pkgdir/usr/share/icons/hicolor/scalable/apps"
  install -D -m644 linux_packaging/modules-load.conf "$pkgdir/usr/lib/modules-load.d/$name.conf"
}
