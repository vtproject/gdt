---
stage: Systems
group: Distribution
info: To determine the technical writer assigned to the Stage/Group associated with this page, see https://about.gitlab.com/handbook/engineering/ux/technical-writing/#assignments
---

# Install GitLab under a relative URL **(FREE SELF)**

While we recommend to install GitLab on its own (sub)domain, sometimes
this is not possible due to a variety of reasons. In that case, GitLab can also
be installed under a relative URL, for example `https://example.com/gitlab`.

This document describes how to run GitLab under a relative URL for installations
from source. If you are using an Omnibus package,
[the steps are different](https://docs.gitlab.com/omnibus/settings/configuration.html#configuring-a-relative-url-for-gitlab). Use this guide along with the
[installation guide](installation.md) if you are installing GitLab for the
first time.

There is no limit to how deeply nested the relative URL can be. For example you
could serve GitLab under `/foo/bar/gitlab/git` without any issues.

Changing the URL on an existing GitLab installation, changes all remote
URLs, so you have to manually edit them in any local repository
that points to your GitLab instance.

The list of configuration files you must change to serve GitLab from a
relative URL is:

- `/home/git/gitlab/config/initializers/relative_url.rb`
- `/home/git/gitlab/config/gitlab.yml`
- `/home/git/gitlab/config/puma.rb`
- `/home/git/gitlab-shell/config.yml`
- `/etc/default/gitlab`

After all the changes, you must recompile the assets and [restart GitLab](../administration/restart_gitlab.md#installations-from-source).

## Relative URL requirements

If you configure GitLab with a relative URL, the assets (including JavaScript,
CSS, fonts, and images) must be recompiled, which can consume a lot of CPU and
memory resources. To avoid out-of-memory errors, you should have at least 2 GB
of RAM available on your computer, and we recommend 4 GB RAM, and four or eight
CPU cores.

See the [requirements](requirements.md) document for more information.

## Enable relative URL in GitLab

NOTE:
Do not make any changes to your web server configuration file regarding
relative URL. The relative URL support is implemented by GitLab Workhorse.

---

Before following the steps below to enable relative URL in GitLab, some
assumptions are made:

- GitLab is served under `/gitlab`
- The directory under which GitLab is installed is `/home/git/`

Make sure to follow all steps below:

1. Optional. If you run short on resources, you can temporarily free up some
   memory by shutting down the GitLab service with the following command:

   ```shell
   sudo service gitlab stop
   ```

1. Create `/home/git/gitlab/config/initializers/relative_url.rb`

   ```shell
   cp /home/git/gitlab/config/initializers/relative_url.rb.sample \
      /home/git/gitlab/config/initializers/relative_url.rb
   ```

   and change the following line:

   ```ruby
   config.relative_url_root = "/gitlab"
   ```

1. Edit `/home/git/gitlab/config/gitlab.yml` and uncomment/change the
   following line:

   ```yaml
   relative_url_root: /gitlab
   ```

1. Edit `/home/git/gitlab/config/puma.rb` and uncomment/change the
   following line:

   ```ruby
   ENV['RAILS_RELATIVE_URL_ROOT'] = "/gitlab"
   ```

1. Edit `/home/git/gitlab-shell/config.yml` and append the relative path to
   the following line:

   ```yaml
   gitlab_url: http://127.0.0.1/gitlab
   ```

1. Make sure you have copied either the supplied systemd services, or the init
   script and the defaults file, as stated in the
   [installation guide](installation.md#install-the-service).
   Then, edit `/etc/default/gitlab` and set in `gitlab_workhorse_options` the
   `-authBackend` setting to read like:

   ```shell
   -authBackend http://127.0.0.1:8080/gitlab
   ```

   NOTE:
   If you are using a custom init script, make sure to edit the above
   GitLab Workhorse setting as needed.

1. [Restart GitLab](../administration/restart_gitlab.md#installations-from-source) for the changes to take effect.

## Disable relative URL in GitLab

To disable the relative URL:

1. Remove `/home/git/gitlab/config/initializers/relative_url.rb`

1. Follow the same as above starting from 2. and set up the
    GitLab URL to one that doesn't contain a relative path.

<!-- ## Troubleshooting

Include any troubleshooting steps that you can foresee. If you know beforehand what issues
one might have when setting this up, or when something is changed, or on upgrading, it's
important to describe those, too. Think of things that may go wrong and include them here.
This is important to minimize requests for support, and to avoid doc comments with
questions that you know someone might ask.

Each scenario can be a third-level heading, e.g. `### Getting error message X`.
If you have none to add when creating a doc, leave this section in place
but commented out to help encourage others to add to it in the future. -->



 >>>>>>> next source file <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


---
stage: Enablement
group: Distribution
info: To determine the technical writer assigned to the Stage/Group associated with this page, see https://about.gitlab.com/handbook/engineering/ux/technical-writing/#designated-technical-writers
comments: false
---

# Omnibus GitLab Documentation **(FREE SELF)**

Omnibus GitLab is a way to package different services and tools required to run GitLab, so that most users can install it without laborious configuration.

## Package information

- [Checking the versions of bundled software](https://docs.gitlab.com/ee/administration/package_information/index.html#checking-the-versions-of-bundled-software)
- [Package defaults](https://docs.gitlab.com/ee/administration/package_information/defaults.html)
- [Components included](https://docs.gitlab.com/ee/development/architecture.html#component-list)
- [Deprecated Operating Systems](https://docs.gitlab.com/ee/administration/package_information/supported_os.html#os-versions-that-are-no-longer-supported)
- [Signed Packages](https://docs.gitlab.com/ee/administration/package_information/signed_packages.html)
- [Deprecation Policy](https://docs.gitlab.com/ee/administration/package_information/deprecation_policy.html)
- [Licenses of bundled dependencies](https://gitlab-org.gitlab.io/omnibus-gitlab/licenses.html)

## Installation

For installation details, see [Installing Omnibus GitLab](installation/index.md).

## Running on a low-resource device (like a Raspberry Pi)

You can run GitLab on supported low-resource computers like the Raspberry Pi 3, but you must tune the settings
to work best with the available resources. Check out the [documentation](settings/rpi.md) for suggestions on what to adjust.

## Maintenance

- [Get service status](maintenance/index.md#get-service-status)
- [Starting and stopping](maintenance/index.md#starting-and-stopping)
- [Invoking Rake tasks](maintenance/index.md#invoking-rake-tasks)
- [Starting a Rails console session](maintenance/index.md#starting-a-rails-console-session)
- [Starting a PostgreSQL superuser `psql` session](maintenance/index.md#starting-a-postgresql-superuser-psql-session)
- [Container registry garbage collection](maintenance/index.md#container-registry-garbage-collection)

## Configuring

- [Configuring the external URL](settings/configuration.md#configure-the-external-url-for-gitlab)
- [Configuring a relative URL for GitLab (experimental)](settings/configuration.md#configure-a-relative-url-for-gitlab)
- [Storing Git data in an alternative directory](settings/configuration.md#store-git-data-in-an-alternative-directory)
- [Changing the name of the Git user group](settings/configuration.md#change-the-name-of-the-git-user-or-group)
- [Specify numeric user and group identifiers](settings/configuration.md#specify-numeric-user-and-group-identifiers)
- [Only start Omnibus GitLab services after a given file system is mounted](settings/configuration.md#start-omnibus-gitlab-services-only-after-a-given-file-system-is-mounted)
- [Disable user and group account management](settings/configuration.md#disable-user-and-group-account-management)
- [Disable storage directory management](settings/configuration.md#disable-storage-directories-management)
- [Failed authentication ban](settings/configuration.md#configure-a-failed-authentication-ban)
- [SMTP](settings/smtp.md)
- [NGINX](settings/nginx.md)
- [LDAP](https://docs.gitlab.com/ee/administration/auth/ldap/index.html)
- [Puma](https://docs.gitlab.com/ee/administration/operations/puma.html)
- [ActionCable](settings/actioncable.md)
- [Redis](settings/redis.md)
- [Logs](settings/logs.md)
- [Database](settings/database.md)
- [Reply by email](https://docs.gitlab.com/ee/administration/reply_by_email.html)
- [Environment variables](settings/environment-variables.md)
- [`gitlab.yml`](settings/gitlab.yml.md)
- [Backups](settings/backups.md)
- [Pages](https://docs.gitlab.com/ee/administration/pages/index.html)
- [SSL](settings/ssl.md)
- [GitLab and Registry](https://docs.gitlab.com/ee/administration/packages/container_registry.html)
- [Configuring an asset proxy server](https://docs.gitlab.com/ee/security/asset_proxy.html)
- [Image scaling](settings/image_scaling.md)

## Upgrading

- [Upgrade guidance](https://docs.gitlab.com/ee/update/package/), including [supported upgrade paths](https://docs.gitlab.com/ee/update/index.html#upgrade-paths).
- [Upgrade from Community Edition to Enterprise Edition](https://docs.gitlab.com/ee/update/package/convert_to_ee.html)
- [Upgrade to the latest version](https://docs.gitlab.com/ee/update/package/#upgrade-using-the-official-repositories)
- [Downgrade to an earlier version](https://docs.gitlab.com/ee/update/package/downgrade.html)
- [Upgrade from a non-Omnibus installation to an Omnibus installation using a backup](update/convert_to_omnibus.md#upgrading-from-non-omnibus-postgresql-to-an-omnibus-installation-using-a-backup)
- [Upgrade from non-Omnibus PostgreSQL to an Omnibus installation in-place](update/convert_to_omnibus.md#upgrading-from-non-omnibus-postgresql-to-an-omnibus-installation-in-place)
- [Upgrade from non-Omnibus MySQL to an Omnibus installation (version 6.8+)](update/convert_to_omnibus.md#upgrading-from-non-omnibus-mysql-to-an-omnibus-installation-version-68)

## Troubleshooting

For troubleshooting details, see [Troubleshooting Omnibus GitLab installation issues](troubleshooting.md).

## Omnibus GitLab developer documentation

See the [development documentation](development/index.md)
