%global pom_version 3.3.2
%global base_version 3.3.2
%global base_release 1

%define jdk_version 1.8.0

%if 0%{?rhel} >= 7 || 0%{?fedora} >= 21
%define maven maven
%else
%define maven apache-maven
%endif

%if %{?build_number:1}%{!?build_number:0}
%define release_version 0.build.%{build_number}
%else
%define release_version %{base_release}
%endif

%global orig_name voms-api-java

Name: voms-api-java
Version: %{base_version}
Release: %{release_version}%{?dist}
Summary: The Virtual Organisation Membership Service Java APIs

Group: System Environment/Libraries
License: ASL 2.0
URL: http://italiangrid.github.com/voms-api-java/
Source0: %{orig_name}-%{version}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:	noarch

BuildRequires:  %{maven}
BuildRequires:  jpackage-utils
BuildRequires:  java-%{jdk_version}-openjdk-devel

Provides:       voms-api-java3
Requires:       jpackage-utils
Requires:       canl-java >= 2.6
Requires:       java-%{jdk_version}-openjdk

%description
The Virtual Organization Membership Service (VOMS) is an attribute authority
which serves as central repository for VO user authorization information,
providing support for sorting users into group hierarchies, keeping track of
their roles and other attributes in order to issue trusted attribute
certificates and SAML assertions used in the Grid environment for
authorization purposes.

This package provides a java client APIs for VOMS.

%package    javadoc
Summary:    Javadoc for the VOMS Java APIs
Group:      Documentation
BuildArch:  noarch
Requires:   jpackage-utils
Requires:   %{name} = %{version}-%{release}

%description javadoc
Virtual Organization Membership Service (VOMS) Java API Documentation.

%prep
%setup -q -n %{orig_name}-%{version}

%build
mvn %{?mvn_settings} -U -Dmaven.test.skip=true clean package

%install
rm -rf %{buildroot} 
mkdir -p %{buildroot}%{_javadir}
mkdir -p %{buildroot}%{_javadocdir}/%{name}-%{pom_version}

install -m 644 target/%{orig_name}-%{pom_version}.jar -t %{buildroot}%{_javadir}
ln -s %{orig_name}-%{pom_version}.jar %{buildroot}%{_javadir}/%{name}.jar
cp -r target/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{pom_version}
ln -s %{name}-%{pom_version} %{buildroot}%{_javadocdir}/%{name}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)

%{_javadir}/%{name}.jar
%{_javadir}/%{orig_name}-%{pom_version}.jar

%doc AUTHORS LICENSE

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}
%doc %{_javadocdir}/%{name}-%{pom_version}

%changelog
* Thu Jan 25 2018 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.3.2-0
- Bumped packaging for 3.3.2 version

* Tue Jun 9 2015 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.6-0
- Bumped packaging for 3.0.6 version

* Wed Dec 10 2014 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.5-1
- Bumped packaging for 3.0.5 version

* Thu Dec 19 2013 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.4-1
- Fix for https://issues.infn.it/browse/VOMS-455
- Caching certificate validator
- Refactored certificate validator builder
- Less stringent mutual exclusion on default AC parser and validator

* Thu Sep 26 2013 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.2-1
- Fix for https://issues.infn.it/browse/VOMS-424
- Adoption of CANL 1.3.0
- Refactored internal AC generator

* Tue Aug 6 2013 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.1-1
- Fix for https://issues.infn.it/jira/browse/VOMS-364

* Wed Oct 24 2012 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 3.0.0-1
- New version of VOMS Java APIs based on CAnL
