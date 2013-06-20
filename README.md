Chube: Object-oriented bindings for the Linode API
============================================================

Chube is a Python library providing an object-oriented interface to the
[Linode API][linode-api], built on top of [linode-python][tjfontaines].
It's very easy to use. But don't take my word for it; check out some
[examples][#examples]!

So far, Chube only supports the **Linode**, **StackScript**, and
**Utility** sections of the API spec. But **DNS** is on its way, and
**NodeBalancer** after that.


<a name="installation"></a>
Installation
------------------------------------------------------------

**Step 1**: Install the PyPI package:

```bash
    pip install chube
```

**Step 2** (optional): Give it your API key:

```bash
    echo -e "---\napi_key: <YOUR API KEY GOES HERE>" > ~/.chube
```

That's it!

To find your API key, log in to the [Linode Manager][linode-mgr], click
on **My Profile**, and scroll down to the **API Key** section.


<a name="usage"></a>
Usage
------------------------------------------------------------

Chube can be used either interactively or as a library.

### Interactive use: chuber.py

Chube is distributed with an executable script called `chuber.py`, which
just drops you into a Python interpreter with an API connection ready to
go. It requires that you've created the file `~/.chube` as described in
the [Installation][#installation] section.

`chuber.py` should be in your `PATH`; look at the [Examples][#examples]
section to see how to use it.

### Library

Chube can also be used as a library. It can either load your API key
from `~/.chube` like so:

```python
    from chube import *
    load_chube_config()
```

Or you can feed it an API key from within the script, like so:

```python
    from chube import *
    chube_api_handler.api_key = "RXIgbWFoIGdlcmQgQVBJIGtlcno"
```


<a name="examples"></a>
Examples
------------------------------------------------------------

If you're like me, you learn best by reading examples. Here are some.

They don't run the whole gamut of what Chube can do, but they should
give you an idea of the conventions to expect.

### List all Linodes whose names start with a given string

```python
    for node in Linode.search(label_begins='foo-'):
        print node.label
```

To list each Linode with its public IP address,

```python
    for node in Linode.search(label_begins='foo-'):
        pub_ip = [ip for ip in node.ipaddresses if ip.is_public]
        print node.label + "\t" + pub_ip
```

### Create a Linode

```python
    p = Plan.find(label="Linode 1024")
    d = Datecenter.find(location_begins="dallas")
    node = Linode.create(plan=p, datacenter=d, payment_term=1)
```

### Set a node's label

```python
    node = Linode.find(label='foo-host')
    node.label = "bar-host"
    node.save()
```

### Add a disk to a Linode, based on a standard distribution

```python
    node = Linode.find(label_begins='some-unique-linode')
    distro = Distribution.find(label="Debian 7")
    disk = node.create_disk(
        linode=node,
        distribution=distro,
        label='foo-disk',
        size=8000,
        root_pass="god")
```

### Boot a Linode

Continuing the last example,

```python
    kern = Kernel.find(label_begins="latest 64 bit")
    config = Config.create(
        linode=node,
        kernel=kern,
        label="foo-config",
        disks=[disk, None, None, None, None, None, None, None, None])
    job = node.boot(config=config)
```

### Wait for a job to finish

Continuing the last example,

```python
    job.wait()
```

### Update a Stackscript

```python
    stackscript = Stackscript.find(is_public=False, label="my-stack-script")
    stackscript.script = "#!/bin/bash\n\necho Hurr durr, I'm a stackscript"
    stackscript.rev_note = "Commit ID 123456789abcdef"
    stackscript.save()
```

### Create a disk based on a Stackscript

```python
    node = Linode.find(label="foo-host")
    distro = Distribution.find(label="Debian 7")
    stackscript = Stackscript.find(is_public=False, label="my-stack-script")
    # This is where you put your UDF responses:
    stack_input = StackscriptInput(param_1="blah blah", param_2="yadda yadda")
    stack_input.param_3 = "hippity hop"

    disk = Disk.create(linode=node,
                       stackscript=stackscript,
                       ss_input=stack_input,
                       distribution=distro,
                       label='foo-disk',
                       size=8000,
                       root_pass="god")
```


[linode-api]: [https://www.linode.com/api/]
[tjfontaines]: [https://github.com/tjfontaine/linode-python]
[linode-mgr]: [https://manager.linode.com]
