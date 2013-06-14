Chube: Object-oriented bindings for the Linode API
=====

Chube lets you interact with the Linode API using a nice and neat
domain space of objects. Here's an example of a session you could
have with Chube:

    you@localhost:~$ chuber
    Python 2.7.2 (default, Oct 11 2012, 20:14:37)
    >>> Linode.search()
    [<Linode api_id=13971, label='foo-01'>, <Linode api_id=20401, label='bar-04'>, <Linode api_id=13972, label='foo-02'>]
    >>>
    >>> nodes = Linode.search(label_begins='foo-')
    [<Linode api_id=13971, label='foo-01'>, <Linode api_id=13972, label='foo-02'>]
    >>>
    >>> for node in nodes:
    ...     print node.ipaddresses[0].address
    ...
    192.168.13.148
    192.168.8.218
    >>>
    >>> plan = Plan.find(label="Linode 1024")
    >>> plan
    <Plan label='Linode 1024'>
    >>> datacenter = Datacenter.find(location_begins="dallas")
    >>> datacenter
    <Datacenter location='Dallas, TX, USA'>
    >>>
    >>> new_node = Linode.create(plan=plan, datacenter=datacenter, payment_term=1)
    >>> new_node
    <Linode api_id=345768, label='linode345768'>
    >>> new_node.label = "web-14"
    >>> new_node.save()
    >>> Linode.find(label="web-14")
    <Linode api_id=345768, label='web-14'>
    >>>
    >>> distro = Distribution.find(label="Debian 7")
    >>> disk = new_node.create_disk(distribution=distro, label="foo_disk", size=2000, root_pass="secret123")
    >>> new_node.pending_jobs
    [<Job api_id=12310126, label='Disk Create From Distribution - Debian 7'>, <Job api_id=12310127, label='Linode Initial Configuration'>]
    >>> new_node.pending_jobs[0].wait()
    >>>
    >>> job = new_node.boot()
    >>> job.wait()
    >>>
    >>> new_node.destroy()

Of course, chube's objects can also be imported into a script with
`from chube import *`.


Installing
-----

    pip install chube
    echo -e "---\napi_key: <YOUR API KEY GOES HERE>" > ~/.chube
