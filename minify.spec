%define		php_min_version 5.2.1
%include	/usr/lib/rpm/macros.php
Summary:	Combines, minifies, and caches JavaScript and CSS files on demand to speed up page loads
Name:		minify
Version:	2.2.0
Release:	1
License:	New BSD License
Group:		Applications/WWW
Source0:	https://github.com/mrclay/minify/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	25b45b2340cae680d169f75c8dcafbc7
Patch0:		paths.patch
Patch1:		pear-firephp.patch
Patch2:		yui-path.patch
# https://github.com/mrclay/minify/pull/69
Patch3:		https://github.com/glensc/minify/compare/contentfunc-params.patch
# Patch3-md5:	bb60232a8a119d1d2eb0caa71dca9207
Source1:	apache.conf
Source2:	lighttpd.conf
URL:		http://code.google.com/p/minify/
BuildRequires:	rpmbuild(macros) >= 1.654
BuildRequires:	unzip
Requires:	php(core) >= %{php_min_version}
Requires:	php(pcre)
Requires:	php-%{name} = %{version}-%{release}
Requires:	webapps
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}
%define		cachedir	/var/cache/%{name}

# skip pear deps
%define		_noautoreq_pear .*Minify/Loader.php FirePHPCore/FirePHP.class.php

%description
Minify is a PHP5 app that helps you follow several of Yahoo!'s Rules
for High Performance Web Sites.

It combines multiple CSS or Javascript files, removes unnecessary
whitespace and comments, and serves them with gzip encoding and
optimal client-side cache headers.

%package -n php-%{name}
Summary:	Minify Classes
Group:		Applications/WWW
Requires:	php(core) >= %{php_min_version}
Requires:	php(ctype)
Requires:	php(date)
Requires:	php(mbstring)
Requires:	php(pcre)
Requires:	php(spl)
Requires:	php-dirs
Suggests:	php-firephp-FirePHPCore

%description -n php-%{name}
Minify Classes.

%package builder
Summary:	Minify URI Builder
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Requires:	php(core) >= %{php_min_version}
Requires:	php(pcre)

%description builder
Minify URI Builder.

%package unit_tests
Summary:	Unit tests for Minify
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}

%description unit_tests
Unit tests for Minify.

%prep
%setup -q
%undos -f php
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%undos UPGRADING.txt

find -type f | xargs chmod a-x

# not needed for functionality
%{__rm} min/lib/Minify/YUI/CssCompressor.java
%{__rm} -r min/lib/MrClay

# php-firephp-FirePHPCore
%{__rm} min/lib/FirePHP.php

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{php_data_dir},%{_sysconfdir},%{_appdir},%{cachedir}}

cp -a min/*.php min/builder $RPM_BUILD_ROOT%{_appdir}
cp -a min/lib/* $RPM_BUILD_ROOT%{php_data_dir}

for config in config.php groupsConfig.php; do
	mv $RPM_BUILD_ROOT{%{_appdir}/$config,%{_sysconfdir}}
	ln -s %{_sysconfdir}/$config $RPM_BUILD_ROOT%{_appdir}
done

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf
cp -p $RPM_BUILD_ROOT%{_sysconfdir}/{apache,httpd}.conf

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%clean
rm -rf $RPM_BUILD_ROOT

%preun
if [ "$1" = 0 ]; then
	echo %{cachedir}/* | xargs rm -rf
fi

%files
%defattr(644,root,root,755)
%doc *.txt
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/config.php
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/groupsConfig.php
%dir %{_appdir}
%{_appdir}/*.php

%dir %attr(771,root,http) %{cachedir}

%files builder
%defattr(644,root,root,755)
%{_appdir}/builder

%files -n php-%{name}
%defattr(644,root,root,755)
%dir %{php_data_dir}/HTTP
%{php_data_dir}/HTTP/ConditionalGet.php
%{php_data_dir}/HTTP/Encoder.php
%{php_data_dir}/CSSmin.php
%{php_data_dir}/DooDigestAuth.php
%{php_data_dir}/JSMin.php
%{php_data_dir}/JSMinPlus.php
%{php_data_dir}/Minify.php
%{php_data_dir}/Minify
