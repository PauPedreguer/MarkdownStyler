%global __provides_exclude_from ^%{_libdir}/markdown-styler/.*$
%global __requires_exclude_from ^%{_libdir}/markdown-styler/.*$

Name:           markdown-styler
Version:        @VERSIO@
Release:        1
Summary:        Generador de documents HTML i PDF amb estil a partir de Markdown
License:        GPL-3.0-or-later
URL:            https://github.com/PauPedreguer/MarkdownStyler
Source0:        markdown-styler.desktop
Source1:        com.github.PauPedreguer.MarkdownStyler.appdata.xml
Source2:        payload.tar.gz
Source3:        LICENSE
Source4:        THIRD-PARTY.md
BuildArch:      x86_64

# Biblioteques del sistema que necessita Qt 6. Les de Qt viatgen al paquet, i
# per això les dependències automàtiques estan desactivades per a eixa carpeta
# (si no, rpm en generaria per a sonames que ja hi són). Ací es demanen pel
# soname, que és el que entenen totes les distribucions amb rpm (Fedora,
# openSUSE, RHEL) sense dependre del nom del paquet.
Requires:       libGL.so.1()(64bit), libEGL.so.1()(64bit)
Requires:       libglib-2.0.so.0()(64bit), libgthread-2.0.so.0()(64bit)
Requires:       libdbus-1.so.3()(64bit), libfontconfig.so.1()(64bit)
Requires:       libfreetype.so.6()(64bit), libharfbuzz.so.0()(64bit)
Requires:       libgraphite2.so.3()(64bit), libpng16.so.16()(64bit)
Requires:       libpcre2-8.so.0()(64bit), libsystemd.so.0()(64bit)
Requires:       libXau.so.6()(64bit), libX11.so.6()(64bit)
Requires:       libX11-xcb.so.1()(64bit), libXext.so.6()(64bit)
Requires:       libxkbcommon.so.0()(64bit), libxkbcommon-x11.so.0()(64bit)
Requires:       libxcb.so.1()(64bit), libxcb-cursor.so.0()(64bit)
Requires:       libxcb-icccm.so.4()(64bit), libxcb-image.so.0()(64bit)
Requires:       libxcb-keysyms.so.1()(64bit), libxcb-randr.so.0()(64bit)
Requires:       libxcb-render.so.0()(64bit), libxcb-render-util.so.0()(64bit)
Requires:       libxcb-shape.so.0()(64bit), libxcb-shm.so.0()(64bit)
Requires:       libxcb-sync.so.1()(64bit), libxcb-util.so.1()(64bit)
Requires:       libxcb-xfixes.so.0()(64bit), libxcb-xkb.so.1()(64bit)
Requires:       libXcomposite.so.1()(64bit), libXdamage.so.1()(64bit)
Requires:       libXfixes.so.3()(64bit), libXi.so.6()(64bit)
Requires:       libXrandr.so.2()(64bit), libXrender.so.1()(64bit)
Requires:       libSM.so.6()(64bit), libXtst.so.6()(64bit)
Requires:       libxml2.so.2()(64bit), libz.so.1()(64bit)
Requires:       libzstd.so.1()(64bit), liblzma.so.5()(64bit)
Requires:       libstdc++.so.6()(64bit)
Recommends:     chromium

%description
Markdown Styler convertix fitxers Markdown en documents HTML i PDF amb
portada, índex i estil professional, pensats per a material de classe.

Els colors d'identitat lliguen cada color amb el seu curs i assignatura, i el
document n'hereta la capçalera. També inclou mode presentació, temes de
ressaltat de codi propis i plantilles i estils personalitzables.

La conversió la fa Pandoc (inclòs al paquet) i el PDF s'obté imprimint el
document amb un navegador basat en Chromium (recomanat: chromium).

%prep
mkdir -p %{_builddir}/payload
tar -xzf %{SOURCE2} -C %{_builddir}/payload

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_libdir}/markdown-styler
cp -a %{_builddir}/payload/. %{buildroot}%{_libdir}/markdown-styler/
install -d %{buildroot}%{_bindir}
ln -s ../$(basename %{_libdir})/markdown-styler/markdown-styler %{buildroot}%{_bindir}/markdown-styler
install -Dpm644 %{SOURCE0} %{buildroot}%{_datadir}/applications/markdown-styler.desktop
install -Dpm644 %{SOURCE1} \
  %{buildroot}%{_datadir}/metainfo/com.github.PauPedreguer.MarkdownStyler.appdata.xml
install -Dpm644 %{SOURCE3} %{buildroot}%{_datadir}/licenses/markdown-styler/LICENSE
install -Dpm644 %{SOURCE4} %{buildroot}%{_datadir}/doc/markdown-styler/THIRD-PARTY.md
for mida in 16 24 32 48 64 128 256 512; do
  install -Dpm644 %{_sourcedir}/icons/${mida}x${mida}.png \
    %{buildroot}%{_datadir}/icons/hicolor/${mida}x${mida}/apps/markdown-styler.png
done

%post
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q %{_datadir}/applications || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q %{_datadir}/applications || :
fi

%files
%license %{_datadir}/licenses/markdown-styler/LICENSE
%doc %{_datadir}/doc/markdown-styler/THIRD-PARTY.md
%{_libdir}/markdown-styler
%{_bindir}/markdown-styler
%{_datadir}/applications/markdown-styler.desktop
%{_datadir}/metainfo/com.github.PauPedreguer.MarkdownStyler.appdata.xml
%{_datadir}/icons/hicolor/*/apps/markdown-styler.png

%changelog
* Fri Nov 13 2026 Pau Palacios Server <pau@users.noreply.github.com> - @VERSIO@-1
- Versió inicial publicada.
