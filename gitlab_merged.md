--- 
 --- 
 source file https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/master/doc/settings/dns.md--- 
 --- 
---
stage: Enablement
group: Distribution
info: To determine the technical writer assigned to the Stage/Group associated with this page, see https://about.gitlab.com/handbook/engineering/ux/technical-writing/#designated-technical-writers
---

# DNS settings **(FREE SELF)**

The Domain Name System (DNS) is the naming system used to match IP addresses
with domain names.

Although you can run a GitLab instance using only its IP address, using a
domain name is:

- Easier to remember and use.
- Required for HTTPS.

  NOTE:
  To take advantage of the [Let's Encrypt integration](--- 
 --- 
 start of linked file https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/master/doc/settings/ssl.md
---
---
---
stage: Enablement
group: Distribution
info: To determine the technical writer assigned to the Stage/Group associated with this page, see https://about.gitlab.com/handbook/engineering/ux/technical-writing/#designated-technical-writers
---

# SSL Configuration **(FREE SELF)**

## Available SSL Configuration Tasks

Omnibus-GitLab supports several common use cases for SSL configuration.

1. Allow `https` connections to GitLab instance services
1. Configure public certificate bundles for external resource connections

## Host Services

Administrators can enable secure http using any method supported by a GitLab service.

| **Service** | **Manual SSL** | **Let's Encrypt** |
|-|-|-|
| Primary GitLab Instance Domain | [Yes](nginx.md#manually-configuring-https) | [Yes](#lets-encrypt-integration) |
| Container Registry | [Yes](https://docs.gitlab.com/ee/administration/packages/container_registry.html#configure-container-registry-under-its-own-domain) | [Yes](#lets-encrypt-integration) |
| Mattermost | [Yes](https://docs.gitlab.com/ee/integration/mattermost/index.html#running-gitlab-mattermost-with-https) | [Yes](#lets-encrypt-integration) |
| GitLab Pages | [Yes](https://docs.gitlab.com/ee/administration/pages/#wildcard-domains-with-tls-support) | No |

### Let's Encrypt Integration

GitLab can be integrated with [Let's Encrypt](https://letsencrypt.org).

#### Primary GitLab Instance

> - Introduced in GitLab 10.5 and disabled by default.
> - Enabled by default in GitLab 10.7 and later if `external_url` is set with
>   the *https* protocol and no certificates are configured.

NOTE:
In order for Let's Encrypt verification to work automatically, ports 80 and 443 will
need to be accessible to the public Let's Encrypt servers that run the validation checks. The validation
[does not work with non-standard ports](https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/3580).
If the environment is private or air-gapped, certbot provides a [manual method](https://eff-certbot.readthedocs.io/en/stable/using.html#manual) to generate certificates for [custom installation](ssl.md#install-custom-public-certificates).

WARNING:
Administrators installing or upgrading to GitLab 10.7 or later and do not plan on using
**Let's Encrypt** should set `letsencrypt['enable'] = false` in `/etc/gitlab/gitlab.rb` to disable.

Add the following entries to `/etc/gitlab/gitlab.rb` to enable **Let's Encrypt**
support for the primary domain:

```ruby
letsencrypt['enable'] = true                      # GitLab 10.5 and 10.6 require this option
external_url "https://gitlab.example.com"         # Must use https protocol
letsencrypt['contact_emails'] = ['foo@email.com'] # Optional
```

NOTE:
Certificates issued by **Let's Encrypt** expire every ninety days. The optional `contact_emails`
setting causes an expiration alert to be sent to the configured address when that expiration date approaches.

#### GitLab Components

> Introduced in GitLab 11.0.

[Follow the steps to enable basic **Let's Encrypt** integration](#lets-encrypt-integration) and
modify `/etc/gitlab/gitlab.rb` with any of the following that apply:

```ruby
registry_external_url "https://registry.example.com"     # container registry, must use https protocol
mattermost_external_url "https://mattermost.example.com" # mattermost, must use https protocol
#registry_nginx['ssl_certificate'] = "path/to/cert"      # Must be absent or commented out
```

The **Let's Encrypt** certificate is created with the GitLab primary
instance as the primary name on the certificate. Additional services
such as the registry are added as alternate names to the same
certificate. Note in the example above, the primary domain is `gitlab.example.com` and
the registry domain is `registry.example.com`. Administrators do not need
to worry about setting up wildcard certificates.

#### Automatic Let's Encrypt Renewal

> [Introduced](https://gitlab.com/gitlab-org/omnibus-gitlab/-/merge_requests/2433) in [GitLab](https://about.gitlab.com/pricing/) 10.7.

WARNING:
Administrators installing or upgrading to GitLab 12.1 or later and plan on using
their own **Let's Encrypt** certificate should set `letsencrypt['enable'] = false` in `/etc/gitlab/gitlab.rb` to
disable automatic renewal. **Otherwise, a `gitlab-ctl reconfigure` may attempt to renew the
certificates, and thus overwrite them.**

Default installations schedule renewals after midnight on every 4th day. The minute is determined by the value in `external_url` to help distribute the load
on the upstream `Let's Encrypt` servers.

Explicitly set renewal times by adding the following to `/etc/gitlab/gitlab.rb`:

```ruby
# This example renews every 7th day at 12:30
letsencrypt['auto_renew_hour'] = "12"
letsencrypt['auto_renew_minute'] = "30"
letsencrypt['auto_renew_day_of_month'] = "*/7"
```

NOTE:
The certificate gets renewed only if it is going to expire in 30 days. For example, if you set it to renew on the 1st of every month at 00:00 and the certificate expires on the 31st, then the certificate will expire before getting renewed.

Disable automatic renewal with the following in `/etc/gitlab/gitlab.rb`:

```ruby
letsencrypt['auto_renew'] = false
```

#### Manual Let's Encrypt Renewal

Renew **Let's Encrypt** certificates manually using ***one*** of the following commands:

```shell
sudo gitlab-ctl reconfigure
```

```shell
sudo gitlab-ctl renew-le-certs
```

WARNING:
GitLab 12.1 or later will attempt to renew any **Let's Encrypt** certificate.
If you plan to use your own **Let's Encrypt** certificate you must set `letsencrypt['enable'] = false`
in `/etc/gitlab/gitlab.rb` to disable integration. **Otherwise the certificate
could be overwritten due to the renewal.**

NOTE:
The above commands require root privileges and only generate a renewal if the certificate is close to expiration.
[Consider the upstream rate limits](https://letsencrypt.org/docs/rate-limits/) if encountering an error during renewal.

### Use an ACME server other than Let's Encrypt

You can use an ACME server other than Let's Encrypt, and configure GitLab to
use that to fetch a certificate. Some services that provide their own ACME
server are:

- [ZeroSSL](https://zerossl.com/documentation/acme/)
- [Buypass](https://www.buypass.com/products/tls-ssl-certificates/go-ssl)
- [SSL.com](https://www.ssl.com/guide/ssl-tls-certificate-issuance-and-revocation-with-acme/)
- [`step-ca`](https://smallstep.com/docs/step-ca)

To configure GitLab to use a custom ACME server:

1. Edit `/etc/gitlab/gitlab.rb` and set the ACME endpoints:

   ```ruby
   external_url 'https://example.com'
   letsencrypt['acme_staging_endpoint'] = 'https://ca.internal/acme/acme/directory'
   letsencrypt['acme_production_endpoint'] = 'https://ca.internal/acme/acme/directory'
   ```

   If the custom ACME server provides it, use a staging endpoint as well.
   Checking the staging endpoint first ensures that the ACME configuration is correct
   before submitting the request to ACME production. Do this to avoid ACME
   rate-limits while working on your configuration.

   The default values are:

   ```plaintext
   https://acme-staging-v02.api.letsencrypt.org/directory
   https://acme-v02.api.letsencrypt.org/directory
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Connecting to External Resources

Some environments connect to external resources for various tasks. Omnibus-GitLab
allows these connections to use secure http (`https`).

### Default Configuration

Omnibus-GitLab ships with the official [CAcert.org](http://www.cacert.org/)
collection of trusted root certification authorities which are used to verify
certificate authenticity.

### Other Certificate Authorities

Omnibus GitLab supports connections to external services with
self-signed certificates.

NOTE:
Custom certificates were introduced in GitLab 8.9.

NOTE:
For installations that use self-signed certificates, Omnibus-GitLab
provides a way to manage these certificates. For more technical details how
this works, see the [details](#details-on-how-gitlab-and-ssl-work)
at the bottom of this page.

#### Install Custom Public Certificates

NOTE:
A perl interpreter is required for `c_rehash` dependency to properly symlink the certificates.
[Perl is currently not bundled in Omnibus GitLab](https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/2275).

1. Generate the **PEM** or **DER** encoded public certificate from your private key certificate.
1. Copy the public certificate file only into the `/etc/gitlab/trusted-certs` directory.
   By default, GitLab expects to find a certificate titled after your GitLab URL with a `.crt`
   extension. For instance, if your server address is `https://gitlab.example.com`, the
   certificate should be named `gitlab.example.com.crt`.

   To specify a different path and file name, you can
   [change the default SSL certificate location](nginx.md#change-the-default-port-and-the-ssl-certificate-locations).
1. [Enable and manually configure HTTPS on NGINX](nginx.md#enable-https) to set up GitLab to use your own certificates.
1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

WARNING:
If using a custom certificate chain, the root and/or intermediate certificates must be put into separate files in `/etc/gitlab/trusted-certs` [due to `c_rehash` creating a hash for the first certificate only](https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/1425).

## Troubleshooting

### Useful OpenSSL Debugging Commands

Sometimes it's helpful to get a better picture of the SSL certificate chain by viewing it directly
at the source. These commands are part of the standard OpenSSL library of tools for diagnostics and
debugging.

NOTE:
GitLab includes its own [custom-compiled version of OpenSSL](#details-on-how-gitlab-and-ssl-work)
that all GitLab libraries are linked against. It's important to run the following commands using
this OpenSSL version.

- Perform a test connection to the host over HTTPS. Replace `HOSTNAME` with your GitLab URL
  (excluding HTTPS), and replace `port` with the port that serves HTTPS connections (usually 443):

  ```shell
  echo | /opt/gitlab/embedded/bin/openssl s_client -connect HOSTNAME:port
  ```

  The `echo` command sends a null request to the server, causing it to close the connection rather
  than wait for additional input. You can use the same command to test remote hosts (for example, a
  server hosting an external repository), by replacing `HOSTNAME:port` with the remote host's domain
  and port number.

  This command's output shows you the certificate chain, any public certificates the server
  presents, along with validation or connection errors if they occur. This makes for a quick check
  for any immediate issues with your SSL settings.

- View a certificate's details in text form using `x509`. Be sure to replace
  `/path/to/certificate.crt` with the certificate's path:

  ```shell
  /opt/gitlab/embedded/bin/openssl x509 -in /path/to/certificate.crt -text -noout
  ```

  For example, GitLab automatically fetches and places certificates acquired from Let's Encrypt at
  `/etc/gitlab/ssl/hostname.crt`. You can use the `x509` command with that path to quickly display
  the certificate's information (for example, the hostname, issuer, validity period, and more).

  If there's a problem with the certificate, [an error occurs](#custom-certificates-missing-or-skipped).

- Fetch a certificate from a server and decode it. This combines both of the above commands to fetch
  the server's SSL certificate and decode it to text:

  ```shell
  echo | /opt/gitlab/embedded/bin/openssl s_client -connect HOSTNAME:port | /opt/gitlab/embedded/bin/openssl x509 -text -noout
  ```

See the [troubleshooting SSL documentation](https://docs.gitlab.com/ee/administration/troubleshooting/ssl.html)
for more examples of troubleshooting SSL problems with OpenSSL.

### Common SSL errors

1. `SSL certificate problem: unable to get local issuer certificate`

    This error indicates the client cannot get the root CA. To fix this, you can either [trust the root CA](#install-custom-public-certificates) of the server you are trying to connect to on the client or [modify the certificate](nginx.md#manually-configuring-https) to present the full chained certificate on the server you are trying to connect to.

    NOTE:
    It is recommended to use the full certificate chain in order to prevent SSL errors when clients connect. The full certificate chain order should consist of the server certificate first, followed by all intermediate certificates, with the root CA last.

1. `unable to verify the first certificate`

    This error indicates that an incomplete certificate chain is being presented by the server. To fix this error, you will need to [replace server's certificate with the full chained certificate](nginx.md#manually-configuring-https). The full certificate chain order should consist of the server certificate first, followed by all intermediate certificates, with the root CA last.

1. `certificate signed by unknown authority`

    This error indicates that the client does not trust the certificate or CA. To fix this error, the client connecting to server will need to [trust the certificate or CA](#install-custom-public-certificates).

1. `SSL certificate problem: self signed certificate in certificate chain`

    This error indicates that the client does not trust the certificate or CA. To fix this error, the client connecting to server will need to [trust the certificate or CA](#install-custom-public-certificates).

### Git-LFS and other embedded services written in ***golang*** report custom certificate signed by unknown authority

NOTE:
In GitLab 11.5, the following workaround is no longer necessary, embedded golang apps now [use the standard GitLab certificate directory automatically](https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/3701).

The `gitlab-workhorse` and other services written in ***golang*** use the **crypto/tls** library from ***golang***
instead of **OpenSSL**.

Add the following entry in `/etc/gitlab/gitlab.rb` to work around the
[issue as reported](https://gitlab.com/gitlab-org/gitlab-workhorse/-/issues/177#note_90203818):

```ruby
gitlab_workhorse['env'] = {
  'SSL_CERT_DIR' => '/opt/gitlab/embedded/ssl/certs/'
}
```

NOTE:
If you have installed GitLab to a path other than `/opt/gitlab/` then modify the entry above
with the correct path in your operating environment.

### Reconfigure Fails Due to Certificates

```shell
ERROR: Not a certificate: /opt/gitlab/embedded/ssl/certs/FILE. Move it from /opt/gitlab/embedded/ssl/certs to a different location and reconfigure again.
```

Check `/opt/gitlab/embedded/ssl/certs` and remove any files other than `README.md` that aren't valid X.509 certificates.

NOTE:
Running `gitlab-ctl reconfigure` constructs symlinks named from the subject hashes
of your custom public certificates and places them in `/opt/gitlab/embedded/ssl/certs/`.
Broken symlinks in `/opt/gitlab/embedded/ssl/certs/` will be automatically removed.
Files other than `cacert.pem` and `README.md` stored in
`/opt/gitlab/embedded/ssl/certs/` will be moved into the `/etc/gitlab/trusted-certs/`.

### Custom Certificates Missing or Skipped

GitLab versions ***8.9.0***, ***8.9.1***, and ***8.9.2*** all mistakenly used the
`/etc/gitlab/ssl/trusted-certs/` directory. This directory is safe to remove if it
is empty. If it still contains custom certificates then move them to `/etc/gitlab/trusted-certs/`
and run `gitlab-ctl reconfigure`.

If no symlinks are created in `/opt/gitlab/embedded/ssl/certs/` and you see
the message "Skipping `cert.pem`" after running `gitlab-ctl reconfigure`, that
means there may be one of four issues:

1. The file in `/etc/gitlab/trusted-certs/` is a symlink
1. The file is not a valid PEM or DER-encoded certificate
1. Perl is not installed on the operating system which is needed for c_rehash to properly symlink certificates
1. The certificate contains the string `TRUSTED`

Test the certificate's validity using the commands below:

```shell
/opt/gitlab/embedded/bin/openssl x509 -in /etc/gitlab/trusted-certs/example.pem -text -noout
/opt/gitlab/embedded/bin/openssl x509 -inform DER -in /etc/gitlab/trusted-certs/example.der -text -noout
```

Invalid certificate files produce the following output:

```shell
unable to load certificate
140663131141784:error:0906D06C:PEM routines:PEM_read_bio:no start line:pem_lib.c:701:Expecting: TRUSTED CERTIFICATE
```

To test if `c_rehash` is not symlinking the certificate due to a missing perl interpreter:

```shell
$ /opt/gitlab/embedded/bin/c_rehash /etc/gitlab/trusted-certs

bash: /opt/gitlab/embedded/bin/c_rehash: /usr/bin/perl: bad interpreter: No such file or directory
```

If you see this message, you will need to install perl with your distribution's package manager.

If you inspect the certificate itself, then look for the string `TRUSTED`:

```plaintext
-----BEGIN TRUSTED CERTIFICATE-----
...
-----END TRUSTED CERTIFICATE-----
```

If it does, like the example above, then try removing the string `TRUSTED` and running `gitlab-ctl reconfigure` again.

### Custom certificates not detected

If after running `gitlab-ctl reconfigure`:

1. no symlinks are created in `/opt/gitlab/embedded/ssl/certs/`;
1. you have placed custom certificates in `/etc/gitlab/trusted-certs/`; and
1. you do not see any skipped or symlinked custom certificate messages

You may be encountering an issue where Omnibus GitLab thinks that the custom
certificates have already been added.

To resolve, delete the trusted certificates directory hash:

```shell
rm /var/opt/gitlab/trusted-certs-directory-hash
```

Then run `gitlab-ctl reconfigure` again. The reconfigure should now detect and symlink
your custom certificates.

### **Let's Encrypt** Certificate signed by unknown authority

The initial implementation of **Let's Encrypt** integration only used the certificate, not the full certificate chain.

Starting in 10.5.4, the full certificate chain will be used. For installs which are already using a certificate, the switchover will not happen until the renewal logic indicates the certificate is near expiration. To force it sooner, run the following

```shell
rm /etc/gitlab/ssl/HOSTNAME*
gitlab-ctl reconfigure
```

Where HOSTNAME is the hostname of the certificate.

### **Let's Encrypt** fails on reconfigure

When you reconfigure, there are common scenarios under which Let's Encrypt may fail:

1. Let's Encrypt may fail if your server isn't able to reach the Let's Encrypt verification servers or vice versa:

   ```shell
   letsencrypt_certificate[gitlab.domain.com] (letsencrypt::http_authorization line 3) had an error: RuntimeError: acme_certificate[staging]  (/opt/gitlab/embedded/cookbooks/cache/cookbooks/letsencrypt/resources/certificate.rb line 20) had an error: RuntimeError: [gitlab.domain.com] Validation failed for domain gitlab.domain.com
   ```

    If you run into issues reconfiguring GitLab due to Let's Encrypt [make sure you have ports 80 and 443 open and accessible](#lets-encrypt-integration).

1. Your domain's Certification Authority Authorization (CAA) record does not allow Let's Encrypt to issue a certificate for your domain. Look for the following error in the reconfigure output:

   ```shell
   letsencrypt_certificate[gitlab.domain.net] (letsencrypt::http_authorization line 5) had an error: RuntimeError: acme_certificate[staging]   (/opt/gitlab/embedded/cookbooks/cache/cookbooks/letsencrypt/resources/certificate.rb line 25) had an error: RuntimeError: ruby_block[create certificate for gitlab.domain.net] (/opt/gitlab/embedded/cookbooks/cache/cookbooks/acme/resources/certificate.rb line 108) had an error: RuntimeError: [gitlab.domain.com] Validation failed, unable to request certificate
   ```

1. If you're using a test domain such as `gitlab.example.com`, without a certificate, you'll see the `unable to request certificate` error shown above. In that case, disable Let's Encrypt by setting `letsencrypt['enable'] = false` in `/etc/gitlab/gitlab.rb`.

You can test your domain using the [Let's Debug](https://letsdebug.net/) diagnostic tool. It can help you figure out why you can't issue a Let's Encrypt certificate.

### Additional troubleshooting

For additional troubleshooting steps, see [Troubleshooting SSL](https://docs.gitlab.com/ee/administration/troubleshooting/ssl.html).

## Details on how GitLab and SSL work

GitLab-Omnibus includes its own library of OpenSSL and links all compiled
programs (e.g. Ruby, PostgreSQL, etc.) against this library. This library is
compiled to look for certificates in `/opt/gitlab/embedded/ssl/certs`.

GitLab-Omnibus manages custom certificates by symlinking any certificate that
gets added to `/etc/gitlab/trusted-certs/` to `/opt/gitlab/embedded/ssl/certs`
using the [c_rehash](https://www.openssl.org/docs/manmaster/man1/c_rehash.html)
tool. For example, let's suppose we add `customcacert.pem` to
`/etc/gitlab/trusted-certs/`:

```shell
$ sudo ls -al /opt/gitlab/embedded/ssl/certs

total 272
drwxr-xr-x 2 root root   4096 Jul 12 04:19 .
drwxr-xr-x 4 root root   4096 Jul  6 04:00 ..
lrwxrwxrwx 1 root root     42 Jul 12 04:19 7f279c95.0 -> /etc/gitlab/trusted-certs/customcacert.pem
-rw-r--r-- 1 root root 263781 Jul  5 17:52 cacert.pem
-rw-r--r-- 1 root root    147 Feb  6 20:48 README
```

Here we see the fingerprint of the certificate is `7f279c95`, which links to
the custom certificate.

What happens when we make an HTTPS request? Let's take a simple Ruby program:

```ruby
#!/opt/gitlab/embedded/bin/ruby
require 'openssl'
require 'net/http'

Net::HTTP.get(URI('https://www.google.com'))
```

This is what happens behind the scenes:

1. The "require `openssl`" line causes the interpreter to load `/opt/gitlab/embedded/lib/ruby/2.3.0/x86_64-linux/openssl.so`.
1. The `Net::HTTP` call then attempts to read the default certificate bundle in `/opt/gitlab/embedded/ssl/certs/cacert.pem`.
1. SSL negotiation occurs.
1. The server sends its SSL certificates.
1. If the certificates that are sent are covered by the bundle, SSL finishes successfully.
1. Otherwise, OpenSSL may validate other certificates by searching for files
   that match their fingerprints inside the predefined certificate directory. For
   example, if a certificate has the fingerprint `7f279c95`, OpenSSL will attempt
   to read `/opt/gitlab/embedded/ssl/certs/7f279c95.0`.

Note that the OpenSSL library supports the definition of `SSL_CERT_FILE` and
`SSL_CERT_DIR` environment variables. The former defines the default
certificate bundle to load, while the latter defines a directory in which to
search for more certificates. These variables should not be necessary if you
have added certificates to the `trusted-certs` directory. However, if for some
reason you need to set them, they can be [defined as environment
variables](environment-variables.md). For example:

```ruby
gitlab_rails['env'] = {"SSL_CERT_FILE" => "/usr/lib/ssl/private/customcacert.pem"}
```

---
---
 end of linked file 
 --- 
 --- 
) (automatic SSL certificates),
  your instance's domain name must be resolvable over the public internet.

## Use a name registrar

To associate a domain name with your instance's IP address, you must specify
one or more DNS records.
Adding a DNS record to your domain's DNS configuration is entirely dependent
on your chosen provider, and out of scope for this document.

Generally, the process is similar to:

1. Visit the control panel of your DNS registrar and add the DNS record.
   It should be one of type:

   - `A`
   - `AAAA`
   - `CNAME`

   The type depends on the underlying architecture of your instance. The most
   common one is the A record.

1. [Test](#successful-dns-query) that the configuration was applied.
1. Use SSH to connect to the server where GitLab is installed.
1. Edit the configuration file `(/etc/gitlab/gitlab.rb)` with your preferred [GitLab settings](#gitlab-settings-that-use-dns).

To learn more about the DNS records, see the
[DNS records overview](https://docs.gitlab.com/ee/user/project/pages/custom_domains_ssl_tls_certification/dns_concepts.html).

## Use a dynamic DNS service

For non-production use, you can use a dynamic DNS service, such as [nip.io](https://nip.io).

We do not recommend these for any production or long-lived instances, as they are often:

- [Insecure](https://github.com/publicsuffix/list/issues/335#issuecomment-261825647)
- [Rate-limited](https://letsencrypt.org/docs/rate-limits/) by Let's Encrypt

## GitLab settings that use DNS

The following GitLab settings correspond to DNS entries.

| GitLab setting | Description | Configuration |
| -------------- | ----------- | ------------- |
| `external_url` | This URL interacts with the main GitLab instance. It's used when cloning over SSH/HTTP/HTTPS and when accessing the web UI. GitLab Runner uses this URL to communicate with the instance. | [Configure the `external_url`](--- 
 --- 
 start of linked file https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/master/doc/settings/configuration.md
---
---
---
stage: Enablement
group: Distribution
info: To determine the technical writer assigned to the Stage/Group associated with this page, see https://about.gitlab.com/handbook/engineering/ux/technical-writing/#designated-technical-writers
---

# Configuration options for the GitLab Linux package **(FREE SELF)**

To configure GitLab, set the relevant options in the `/etc/gitlab/gitlab.rb` file.

[`gitlab.rb.template`](https://gitlab.com/gitlab-org/omnibus-gitlab/blob/master/files/gitlab-config-template/gitlab.rb.template)
contains a complete list of available options. New installations have all the
options of the template listed in `/etc/gitlab/gitlab.rb` by default.

For a list of default settings, see the
[package defaults](https://docs.gitlab.com/ee/administration/package_information/defaults.html).

## Configure the external URL for GitLab

To display the correct repository clone links to your users,
you must provide GitLab with the URL your users use to reach the repository.
You can use the IP of your server, but a Fully Qualified Domain Name (FQDN)
is preferred. See the [DNS documentation](dns.md)
for more details about the use of DNS in a self-managed GitLab instance.

To change the external URL:

1. Optional. Before you change the external URL, determine if you have previously
   defined a [custom **Home page URL** or **After sign-out path**](https://docs.gitlab.com/ee/user/admin_area/settings/sign_in_restrictions.html#sign-in-information).
   Both of these settings might cause unintentional redirecting after configuring
   a new external URL. If you have defined any URLs, remove them completely.

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   external_url "http://gitlab.example.com"
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

1. After you change the external URL, we recommended you also
   [invalidate the Markdown cache](https://docs.gitlab.com/ee/administration/invalidate_markdown_cache.html).

### Specify the external URL at the time of installation

If you use the GitLab Linux package, you can set up your GitLab instance
with the minimum number of commands by using the `EXTERNAL_URL` environment variable.
If this variable is set, it is automatically detected and its value is written
as `external_url` in the `gitlab.rb` file.

The `EXTERNAL_URL` environment variable affects only the installation and upgrade
of packages. For regular reconfigure runs, the value
in `/etc/gitlab/gitlab.rb` is used.

As part of package updates, if you have `EXTERNAL_URL` variable set
inadvertently, it replaces the existing value in `/etc/gitlab/gitlab.rb`
without any warning. So, we recommended not to set the variable globally, but
rather pass it specifically to the installation command:

```shell
sudo EXTERNAL_URL="https://gitlab.example.com" apt-get install gitlab-ee
```

## Configure a relative URL for GitLab

NOTE:
For installations from source, there is a
[separate document](https://docs.gitlab.com/ee/install/relative_url.html).

While we recommended installing GitLab in its own (sub)domain, sometimes
it is not possible. In that case, GitLab can also
be installed under a relative URL, for example, `https://example.com/gitlab`.

By changing the URL, all remote URLs change as well, so you must
manually edit them in any local repository that points to your GitLab instance.

To enable relative URL in GitLab:

1. Set the `external_url` in `/etc/gitlab/gitlab.rb`:

   ```ruby
   external_url "https://example.com/gitlab"
   ```

   In this example, the relative URL under which GitLab is served is
   `/gitlab`. Change it to your liking.

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

If you have any issues, see the [troubleshooting section](#relative-url-troubleshooting).

## Load external configuration file from non-root user

Omnibus GitLab package loads all configuration from `/etc/gitlab/gitlab.rb` file.
This file has strict file permissions and is owned by the `root` user. The reason for strict permissions
and ownership is that `/etc/gitlab/gitlab.rb` is being executed as Ruby code by the `root` user during `gitlab-ctl reconfigure`. This means
that users who have to write access to `/etc/gitlab/gitlab.rb` can add configuration that is executed as code by `root`.

In certain organizations, it is allowed to have access to the configuration files but not as the root user.
You can include an external configuration file inside `/etc/gitlab/gitlab.rb` by specifying the path to the file:

```ruby
from_file "/home/admin/external_gitlab.rb"
```

Code you include into `/etc/gitlab/gitlab.rb` using `from_file` runs with `root` privileges when you run `sudo gitlab-ctl reconfigure`.
Any configuration that is set in `/etc/gitlab/gitlab.rb` after `from_file` is included, takes precedence over the configuration from the included file.

## Store Git data in an alternative directory

By default, Omnibus GitLab stores the Git repository data under
`/var/opt/gitlab/git-data`. The repositories are stored in a subfolder called
`repositories`.

To change the location of the `git-data` parent directory:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   git_data_dirs({ "default" => { "path" => "/mnt/nas/git-data" } })
   ```

   You can also add more than one Git data directories:

   ```ruby
   git_data_dirs({
     "default" => { "path" => "/var/opt/gitlab/git-data" },
     "alternative" => { "path" => "/mnt/nas/git-data" }
   })
   ```

   The target directories and any of its subpaths must not be a symlink.

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

1. Optional. If you already have existing Git repositories in `/var/opt/gitlab/git-data`, you
   can move them to the new location:
   1. Prevent users from writing to the repositories while you move them:

      ```shell
      sudo gitlab-ctl stop
      ```

   1. Sync the repositories to the new location. Note there is _no_ slash behind
      `repositories`, but there _is_ a slash behind `git-data`:

      ```shell
      sudo rsync -av --delete /var/opt/gitlab/git-data/repositories /mnt/nas/git-data/
      ```

   1. Reconfigure to start the necessary processes and fix any wrong permissions:

      ```shell
      sudo gitlab-ctl reconfigure
      ```

   1. Double-check the directory layout in `/mnt/nas/git-data/`. The expected output
      should be `repositories`:

      ```shell
      sudo ls /mnt/nas/git-data/
      ```

   1. Start GitLab and verify that you can browse through the repositories in
      the web interface:

      ```shell
      sudo gitlab-ctl start
      ```

If you're running Gitaly on its own server remember to also include the
`gitaly_address` for each Git data directory. See [the documentation on
configuring Gitaly](https://docs.gitlab.com/ee/administration/gitaly/configure_gitaly.html#configure-gitaly-clients).

If you're not looking to move all repositories, but instead want to move specific
projects between existing repository storages, use the
[Edit Project API](https://docs.gitlab.com/ee/api/projects.html#edit-project)
endpoint and specify the `repository_storage` attribute.

## Change the name of the Git user or group

NOTE:
We do not recommend changing the user or group of an existing installation because it can cause unpredictable side-effects.

By default, Omnibus GitLab uses the user name `git` for Git GitLab Shell login,
ownership of the Git data itself, and SSH URL generation on the web interface.
Similarly, the `git` group is used for group ownership of the Git data.

To change the user and group:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   user['username'] = "gitlab"
   user['group'] = "gitlab"
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

If you are changing the username of an existing installation, the reconfigure run
doesn't change the ownership of the nested directories, so you must do that manually.
Make sure that the new user can access the `repositories` and `uploads` directories.

## Specify numeric user and group identifiers

Omnibus GitLab creates users for GitLab, PostgreSQL, Redis, NGINX, etc. To
specify the numeric identifiers for these users:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   user['uid'] = 1234
   user['gid'] = 1234
   postgresql['uid'] = 1235
   postgresql['gid'] = 1235
   redis['uid'] = 1236
   redis['gid'] = 1236
   web_server['uid'] = 1237
   web_server['gid'] = 1237
   registry['uid'] = 1238
   registry['gid'] = 1238
   mattermost['uid'] = 1239
   mattermost['gid'] = 1239
   prometheus['uid'] = 1240
   prometheus['gid'] = 1240
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

1. Optional. If you're changing `user['uid']` and `user['gid']`, make sure to update the uid/guid of any files not managed by Omnibus directly, for example the logs:

```shell
find /var/log/gitlab -uid <old_uid> | xargs -I:: chown git ::
find /var/log/gitlab -gid <old_uid> | xargs -I:: chgrp git ::
find /var/opt/gitlab -uid <old_uid> | xargs -I:: chown git ::
find /var/opt/gitlab -gid <old_uid> | xargs -I:: chgrp git ::
```

## Disable user and group account management

By default, Omnibus GitLab creates system user and group accounts,
as well as keeping the information updated.
These system accounts run various components of the package.
Most users don't need to change this behavior.
However, if your system accounts are managed by other software, for example LDAP, you
might need to disable account management done by the GitLab package.

By default, the Omnibus GitLab package expects that following users and groups to exist:

| Linux user and group | Required                                | Description                                                          |
| -------------------- | --------------------------------------- | -------------------------------------------------------------------- |
| `git`                | Yes                                     | GitLab user/group                                                    |
| `gitlab-www`         | Yes                                     | Web server user/group                                                |
| `gitlab-redis`       | Only when using the packaged Redis      | Redis user/group for GitLab                                          |
| `gitlab-psql`        | Only when using the packaged PostgreSQL | PostgreSQL user/group                                                |
| `gitlab-prometheus`  | Yes                                     | Prometheus user/group for Prometheus monitoring and various exporters|
| `mattermost`         | Only when using GitLab Mattermost       | GitLab Mattermost user/group                                         |
| `registry`           | Only when using GitLab Registry         | GitLab Registry user/group                                           |
| `gitlab-consul`      | Only when using GitLab Consul           | GitLab Consul user/group                                             |

To disable user and group accounts management:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   manage_accounts['enable'] = false
   ```

1. Optional. You can also use different user/group names, but then you must specify the user/group details:

   ```ruby
   # GitLab
   user['username'] = "custom-gitlab"
   user['group'] = "custom-gitlab"
   user['shell'] = "/bin/sh"
   user['home'] = "/var/opt/custom-gitlab"

   # Web server
   web_server['username'] = 'webserver-gitlab'
   web_server['group'] = 'webserver-gitlab'
   web_server['shell'] = '/bin/false'
   web_server['home'] = '/var/opt/gitlab/webserver'

   # Postgresql (not needed when using external Postgresql)
   postgresql['username'] = "postgres-gitlab"
   postgresql['group'] = "postgres-gitlab"
   postgresql['shell'] = "/bin/sh"
   postgresql['home'] = "/var/opt/postgres-gitlab"

   # Redis (not needed when using external Redis)
   redis['username'] = "redis-gitlab"
   redis['group'] = "redis-gitlab"
   redis['shell'] = "/bin/false"
   redis['home'] = "/var/opt/redis-gitlab"

   # And so on for users/groups for GitLab Mattermost
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Move the home directory for a user

For the GitLab user, we recommended that the home directory
is set in local disk and not on a shared storage like NFS, for better performance. When setting it in
NFS, Git requests must make another network request to read the Git
configuration and this increases latency in Git operations.

To move an existing home directory, GitLab services need to be stopped and some downtime is required:

1. Stop GitLab:

   ```shell
   gitlab-ctl stop
   ```

1. Stop the runit server:

   ```shell
   sudo systemctl stop gitlab-runsvdir
   ```

1. Change the home directory:

   ```shell
   usermod -d /path/to/home <username>
   ```

   If you had existing data, you need to manually copy/rsync it to the new location:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   user['home'] = "/var/opt/custom-gitlab"
   ```

1. Start the runit server:

   ```shell
   sudo systemctl start gitlab-runsvdir
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Disable storage directories management

The Omnibus GitLab package takes care of creating all the necessary directories
with the correct ownership and permissions, as well as keeping this updated.

Some of the directories hold large amounts of data, so in certain setups,
those directories are most likely mounted on an NFS (or some other) share.

Some types of mounts don't allow automatic creation of directories by the root user
(default user for initial setup), for example NFS with `root_squash` enabled on the
share. To work around this, the Omnibus GitLab package attempts to create
those directories using the directory's owner user.

### Disable the `/etc/gitlab` directory management

If you have the `/etc/gitlab` directory mounted, you can turn off the management of
that directory:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   manage_storage_directories['manage_etc'] = false
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

### Disable the `/var/opt/gitlab` directory management

If you are mounting all GitLab storage directories, each on a separate mount,
you should completely disable the management of storage directories.

The Omnibus GitLab package expects these directories to exist
on the file system. It is up to you to create and set correct
permissions if this setting is set.

Enabling this setting prevents the creation of the following directories:

| Default location                                       | Permissions   | Ownership        | Purpose                            |
|--------------------------------------------------------|---------------|------------------|------------------------------------|
| `/var/opt/gitlab/git-data`                             | `0700`        | `git:git`        | Holds repositories directory       |
| `/var/opt/gitlab/git-data/repositories`                | `2770`        | `git:git`        | Holds Git repositories             |
| `/var/opt/gitlab/gitlab-rails/shared`                  | `0751`        | `git:gitlab-www` | Holds large object directories     |
| `/var/opt/gitlab/gitlab-rails/shared/artifacts`        | `0700`        | `git:git`        | Holds CI artifacts                 |
| `/var/opt/gitlab/gitlab-rails/shared/external-diffs`   | `0700`        | `git:git`        | Holds external merge request diffs |
| `/var/opt/gitlab/gitlab-rails/shared/lfs-objects`      | `0700`        | `git:git`        | Holds LFS objects                  |
| `/var/opt/gitlab/gitlab-rails/shared/packages`         | `0700`        | `git:git`        | Holds package repository           |
| `/var/opt/gitlab/gitlab-rails/shared/dependency_proxy` | `0700`        | `git:git`        | Holds dependency proxy             |
| `/var/opt/gitlab/gitlab-rails/shared/terraform_state`  | `0700`        | `git:git`        | Holds terraform state              |
| `/var/opt/gitlab/gitlab-rails/shared/ci_secure_files`  | `0700`        | `git:git`        | Holds uploaded secure files        |
| `/var/opt/gitlab/gitlab-rails/shared/pages`            | `0750`        | `git:gitlab-www` | Holds user pages                   |
| `/var/opt/gitlab/gitlab-rails/uploads`                 | `0700`        | `git:git`        | Holds user attachments             |
| `/var/opt/gitlab/gitlab-ci/builds`                     | `0700`        | `git:git`        | Holds CI build logs                |
| `/var/opt/gitlab/.ssh`                                 | `0700`        | `git:git`        | Holds authorized keys              |

To disable the management of storage directories:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   manage_storage_directories['enable'] = false
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Start Omnibus GitLab services only after a given file system is mounted

If you want to prevent Omnibus GitLab services (NGINX, Redis, Puma, etc.)
from starting before a given file system is mounted:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   # wait for /var/opt/gitlab to be mounted
   high_availability['mountpoint'] = '/var/opt/gitlab'
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Configure the runtime directory

When Prometheus monitoring is enabled, the GitLab Exporter conducts measurements
of each Puma process (Rails metrics). Every Puma process needs to write
a metrics file to a temporary location for each controller request.
Prometheus then collects all these files and process their values.

To avoid creating disk I/O, the Omnibus GitLab package uses a
runtime directory.

During `reconfigure`, the package check if `/run` is a `tmpfs` mount.
If it is not, the following warning is shown and Rails metrics is disabled:

```plaintext
Runtime directory '/run' is not a tmpfs mount.
```

To enable the Rails metrics again:

1. Edit `/etc/gitlab/gitlab.rb` to create a `tmpfs` mount
   (note that there is no `=` in the configuration):

   ```ruby
   runtime_dir '/path/to/tmpfs'
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Configure a failed authentication ban

You can configure a [failed authentication ban](https://docs.gitlab.com/ee/security/rate_limits.html#failed-authentication-ban-for-git-and-container-registry)
for Git and the container registry:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   gitlab_rails['rack_attack_git_basic_auth'] = {
     'enabled' => true,
     'ip_whitelist' => ["127.0.0.1"],
     'maxretry' => 10, # Limit the number of Git HTTP authentication attempts per IP
     'findtime' => 60, # Reset the auth attempt counter per IP after 60 seconds
     'bantime' => 3600 # Ban an IP for one hour (3600s) after too many auth attempts
   }
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

The following settings can be configured:

- `enabled`: By default this is set to `false`. Set this to `true` to enable Rack Attack.
- `ip_whitelist`: IPs to not block. They must be formatted as strings in a
  Ruby array. CIDR notation is supported in GitLab 12.1 and later.
  For example, `["127.0.0.1", "127.0.0.2", "127.0.0.3", "192.168.0.1/24"]`.
- `maxretry`: The maximum amount of times a request can be made in the
  specified time.
- `findtime`: The maximum amount of time that failed requests can count against an IP
  before it's added to the denylist (in seconds).
- `bantime`: The total amount of time that an IP is blocked (in seconds).

## Disable automatic cache cleaning during installation

If you have large GitLab installation, you might not want to run a `rake cache:clear` task
as it can take a long time to finish. By default, the cache clear task runs automatically
during reconfigure.

To disable automatic cache cleaning during installation:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   # This is an advanced feature used by large gitlab deployments where loading
   # whole RAILS env takes a lot of time.
   gitlab_rails['rake_cache_clear'] = false
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Error Reporting and Logging with Sentry

[Sentry](https://sentry.io) is an error reporting and logging tool which can be
used as SaaS or on premise. It's Open Source, and you can [browse its source code
repositories](https://github.com/getsentry).

To configure Sentry:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   gitlab_rails['sentry_enabled'] = true
   gitlab_rails['sentry_dsn'] = 'https://<key>@sentry.io/<project>'
   gitlab_rails['sentry_clientside_dsn'] = 'https://<key>@sentry.io/<project>'
   gitlab_rails['sentry_environment'] = 'production'
   ```

   The [Sentry environment](https://docs.sentry.io/product/sentry-basics/environments/)
   can be used to track errors and issues across several deployed GitLab
   environments, for example lab, development, staging, production.

1. Optional. To set custom [Sentry tags](https://docs.sentry.io/product/sentry-basics/guides/enrich-data/)
   on every event sent from a particular server, the `GITLAB_SENTRY_EXTRA_TAGS`
   environment variable can be set. This variable is a JSON-encoded hash representing any
   tags that should be passed to Sentry for all exceptions from that server.

   For instance, setting:

   ```ruby
   gitlab_rails['env'] = {
     'GITLAB_SENTRY_EXTRA_TAGS' => '{"stage": "main"}'
   }
   ```

   Would add the `stage` tag with a value of `main`.

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Set a Content Delivery Network URL

Service static assets with a Content Delivery Network (CDN) or asset host
using `gitlab_rails['cdn_host']`. This configures a [Rails asset host](https://guides.rubyonrails.org/configuring.html#config-asset-host).

To set a CDN/asset host:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   gitlab_rails['cdn_host'] = 'https://mycdnsubdomain.fictional-cdn.com'
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

Additional documentation for configuring common services to act as an asset host
is tracked in [this issue](https://gitlab.com/gitlab-org/omnibus-gitlab/-/issues/5708).

## Set a Content Security Policy

Setting a Content Security Policy (CSP) can help thwart JavaScript
cross-site scripting (XSS) attacks. See [the Mozilla documentation on
CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) for more
details.

GitLab 12.2 added support for [CSP and nonce-source with inline
JavaScript](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/script-src).
It is [not configured on by default
yet](https://gitlab.com/gitlab-org/gitlab/-/issues/30720).

NOTE:
Improperly configuring the CSP rules could prevent GitLab from working
properly. Before rolling out a policy, you may also want to change
`report_only` to `true` to test the configuration.

To add a CSP:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   gitlab_rails['content_security_policy'] = {
       enabled: true,
       report_only: false
   }
   ```

   GitLab automatically provides secure default values for the CSP.

   To add a custom CSP:

   ```ruby
   gitlab_rails['content_security_policy'] = {
       enabled: true,
       report_only: false,
       directives: {
         default_src: "'none'",
         script_src: "https://example.com"
       }
   }
   ```

   [In GitLab 14.9 and later](https://gitlab.com/gitlab-org/gitlab/-/merge_requests/80303), secure default values
   are used for the directives that aren't explicitly configured.

   To unset a CSP directive, set a value of `false`.

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

## Set initial root password on installation

The initial password for the administrator user `root` can be set at the installation time
with the `GITLAB_ROOT_PASSWORD` environment variable:

```shell
sudo GITLAB_ROOT_PASSWORD="<strongpassword>" EXTERNAL_URL="http://gitlab.example.com" apt install gitlab-ee
```

## Set allowed hosts to prevent host header attacks

To prevent GitLab from accepting a host header other than
what's intended:

1. Edit `/etc/gitlab/gitlab.rb`:

   ```ruby
   gitlab_rails['allowed_hosts'] = ['gitlab.example.com']
   ```

1. Reconfigure GitLab:

   ```shell
   sudo gitlab-ctl reconfigure
   ```

There are no known security issues in GitLab caused by not configuring `allowed_hosts`,
but it's recommended for defense in depth against potential [host header attacks](https://portswigger.net/web-security/host-header).

## Related topics

- [Disable impersonation](https://docs.gitlab.com/ee/api/index.html#disable-impersonation)
- [Set up LDAP sign-in](https://docs.gitlab.com/ee/administration/auth/ldap/index.html)
- [Smartcard authentication](https://docs.gitlab.com/ee/administration/auth/smartcard.html)
- [Set up NGINX](nginx.md) for things like:
  - Set up HTTPS
  - Redirect `HTTP` requests to `HTTPS`
  - Change the default port and the SSL certificate locations
  - Set the NGINX listen address or addresses
  - Insert custom NGINX settings into the GitLab server block
  - Insert custom settings into the NGINX configuration
  - Enable `nginx_status`
- [Use a non-packaged web-server](nginx.md#using-a-non-bundled-web-server)
- [Use a non-packaged PostgreSQL database management server](database.md)
- [Use a non-packaged Redis instance](redis.md)
- [Add `ENV` vars to the GitLab runtime environment](environment-variables.md)
- [Change GitLab.yml settings](gitlab.yml.md)
- [Send application email via SMTP](smtp.md)
- [Set up OmniAuth (Google, Twitter, GitHub login)](https://docs.gitlab.com/ee/integration/omniauth.html)
- [Adjust Puma settings](https://docs.gitlab.com/ee/administration/operations/puma.html)

## Troubleshooting

### Relative URL troubleshooting

If you notice any issues with GitLab assets appearing broken after moving to a
relative URL configuration (like missing images or unresponsive components),
please raise an issue in [GitLab](https://gitlab.com/gitlab-org/gitlab)
with the `Frontend` label.

### `Mixlib::ShellOut::ShellCommandFailed: linux_user[GitLab user and group]`

When [moving the home directory for a user](#move-the-home-directory-for-a-user),
if the runit service is not stopped and the home directories are not manually
moved for the user, GitLab will encounter an error while reconfiguring:

```plaintext
account[GitLab user and group] (gitlab::users line 28) had an error: Mixlib::ShellOut::ShellCommandFailed: linux_user[GitLab user and group] (/opt/gitlab/embedded/cookbooks/cache/cookbooks/package/resources/account.rb line 51) had an error: Mixlib::ShellOut::ShellCommandFailed: Expected process to exit with [0], but received '8'
---- Begin output of ["usermod", "-d", "/var/opt/gitlab", "git"] ----
STDOUT:
STDERR: usermod: user git is currently used by process 1234
---- End output of ["usermod", "-d", "/var/opt/gitlab", "git"] ----
Ran ["usermod", "-d", "/var/opt/gitlab", "git"] returned 8
```

Make sure to stop `runit` before moving the home directory.

---
---
 end of linked file 
 --- 
 --- 
). |
| `registry_external_url` | This URL is used to interact with the [Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/). It can be used by the Let's Encrypt integration. This URL can also use the same DNS entry as `external_url` but on a different port. | [Configure the `registry_external_url`](https://docs.gitlab.com/ee/administration/packages/container_registry.html#container-registry-domain-configuration). |
| `mattermost_external_url` | This URL is used for the [bundled Mattermost](https://docs.gitlab.com/ee/integration/mattermost/) software. It can be used by the Let's Encrypt integration. | [Configure the `mattermost_external_url`](https://docs.gitlab.com/ee/integration/mattermost/#getting-started). |
| `pages_external_url` | By default, projects that use [GitLab Pages](https://docs.gitlab.com/ee/user/project/pages/) deploy to a sub-domain of this value. | [Configure the `pages_external_url`](https://docs.gitlab.com/ee/administration/pages/#configuration).
| Auto DevOps domain | If you use Auto DevOps to deploy projects, this domain can be used to deploy software. It can be defined at an instance, or cluster level. This is configured using the GitLab UI, and not in `/etc/gitlab/gitlab.rb`. | [Configure the Auto DevOps domain](https://docs.gitlab.com/ee/topics/autodevops/requirements.html#auto-devops-base-domain). |

## Troubleshooting

If you have issues accessing a particular component, or if the Let's
Encrypt integration is failing, you might have a DNS issue. You can use the
[dig](https://en.wikipedia.org/wiki/Dig_(command)) tool to determine if
DNS is causing a problem.

### Successful DNS query

This example uses the [Public Cloudflare DNS resolver](https://www.cloudflare.com/learning/dns/what-is-1.1.1.1/) to ensure that the query is globally resolvable. However, other public resolvers like the [Google Public DNS resolver](https://developers.google.com/speed/public-dns) are also available.

```shell
$ dig registry.gitlab.com @1.1.1.1

; <<>> DiG 9.16.1-Ubuntu <<>> registry.gitlab.com @1.1.1.1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 4128
;; flags: qr rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;registry.gitlab.com.   IN  A

;; ANSWER SECTION:
registry.gitlab.com.  37  IN  A  104.18.27.123
registry.gitlab.com.  37  IN  A  104.18.26.123

;; Query time: 4 msec
;; SERVER: 1.1.1.1#53(1.1.1.1)
;; WHEN: Wed Jul 06 10:03:59 CEST 2022
;; MSG SIZE  rcvd: 80

```

Make sure that the status is `NOERROR`, and that the `ANSWER SECTION` has the actual results.

### Failed DNS query

```shell
$ dig fake.gitlab.com @1.1.1.1

; <<>> DiG 9.16.1-Ubuntu <<>> fake.gitlab.com @1.1.1.1
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 1502
;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;fake.gitlab.com.    IN A

;; AUTHORITY SECTION:
gitlab.com.   3600 IN SOA diva.ns.cloudflare.com. dns.cloudflare.com. 2282080190 10000 2400 604800 3600

;; Query time: 8 msec
;; SERVER: 1.1.1.1#53(1.1.1.1)
;; WHEN: Wed Jul 06 10:06:53 CEST 2022
;; MSG SIZE  rcvd: 103
```

In this example, the `status` is `NXDOMAIN`, and there is no `ANSWER SECTION`. The `SERVER` field tells you which DNS server was queried for the answer, in this case the [Public Cloudflare DNS resolver](https://www.cloudflare.com/learning/dns/what-is-1.1.1.1/).

### Use a wildcard DNS entry

It is possible use a wildcard DNS for the [URL attributes](#gitlab-settings-that-use-dns),
but you must provide the full domain name for each one.

The Let's Encrypt integration does not fetch a wildcard certificate. You must do this
[on your own](https://certbot.eff.org/faq/#does-let-s-encrypt-issue-wildcard-certificates).
