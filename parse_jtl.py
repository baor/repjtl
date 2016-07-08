# -*- coding: utf-8 -*-

'''

example:
python repjtl.py example2.jtl example3.jtl


Attribute	Content
by	Bytes
de	Data encoding
dt	Data type
ec	Error count (0 or 1, unless multiple samples are aggregated)
hn	Hostname where the sample was generated
it	Idle Time = time not spent sampling (milliseconds) (generally 0)
lb	Label
lt	Latency = time to initial response (milliseconds) - not all samplers support this
ct	Connect Time = time to establish the connection (milliseconds) - not all samplers support this
na	Number of active threads for all thread groups
ng	Number of active threads in this group
rc	Response Code (e.g. 200)
rm	Response Message (e.g. OK)
s	Success flag (true/false)
sc	Sample count (1, unless multiple samples are aggregated)
t	Elapsed time (milliseconds)
tn	Thread Name
ts	timeStamp (milliseconds since midnight Jan 1, 1970 UTC)
varname	Value of the named variable (versions of JMeter after 2.3.1)

Setup:

pip install lxml argparse numpy fpdf math

ubuntu: sudo apt-get install libpng-dev libfreetype6-dev
rhel: yum install libpng-devel

then -->>

pip install matplotlib
'''

_TRANSACTION_PREFIX = 'TrC: '

MAX_LENGTH = 100  # max zabbix lenght == 128


def parse_sampler(elem):
    sampler = dict()
    sampler["tag"] = elem.tag
    for attr in elem.attrib:
            sampler[attr] = elem.attrib[attr]
    for child in elem.iterchildren():
        if child.tag == "assertionResult":
            for child2 in child.iterchildren():
                if child2.tag == "failureMessage":
                    if "failureMessage" not in sampler:
                        sampler["failureMessage"] = ""
                    sampler["failureMessage"] += "%s. %s. %s\r\n" % (child.tag, child2.tag, child2.text)
        elif child.tag == "httpSample" and child.attrib["s"] == "false":
            if "failureMessage" not in sampler:
                sampler["failureMessage"] = ""
            sampler["failureMessage"] += "%s. %s\r\n" % (child.attrib["rc"], child.attrib["rm"])
    return sampler


def parse_sampler_to_touple(sampler):

    if sampler["s"] == "true":
        value = sampler["t"]
    elif sampler["rc"] != "200":
        value = "%s. %s" % (sampler["rc"], sampler["rm"])
    elif "failureMessage" in sampler:
        value = sampler["failureMessage"]
    else:
        value = "unknown error. ts: %s tn: %s" % (sampler["ts"], sampler["tn"])
    return sampler["ts"], sampler["s"], value


def parse_tree_into_labels_and_threads_dict(tree, transactions_only=False):
    """
    :param tree: jtl file with report
    :param transactions_only: flag for transactions only
    :return: dictionary {"label":[(timestamp, isSuccess, value)]} where value can be response time or error text
    """
    list_of_samplers = []
    for action, elem_test_results in tree:
        for child in elem_test_results.iterchildren():
            list_of_samplers.append(parse_sampler(child))
            child.clear()
    del tree

    labels_dict = {}
    thread_name_dict = {}
    for sampler in list_of_samplers:
        if "tn" in sampler:
            # remove last word like 111-222
            thread_name = " ".join(sampler["tn"].split()[:-1])
            if thread_name not in thread_name_dict:
                thread_name_dict[thread_name] = []
            thread_name_dict[thread_name].append((sampler["ts"], sampler["ng"]))
        if "lb" in sampler:
            label = sampler["lb"].strip()[:MAX_LENGTH]

            if transactions_only and not label.startswith(_TRANSACTION_PREFIX):
                continue
            if label not in labels_dict:
                labels_dict[label] = []
            labels_dict[label].append(parse_sampler_to_touple(sampler))
    return labels_dict, thread_name_dict


def get_errors_from_labels(labels):
    errors = {}
    for label, touple_arr in labels.items():
        for ts, s, value in touple_arr:
            if s != "true":
                if label not in errors:
                    errors[label] = []
                errors[label].append(value)
    return errors
