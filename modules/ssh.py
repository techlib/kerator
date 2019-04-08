#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import config


def create_ssh_client(server, user):
    """
    Returns ssh client.
    :param server: server to which we want to connect via SSH
    :param user: user, under which we are connection to the server via SSH
    :return: SSH client instance
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(server, username=user)
    return client


def send_update_to_server(client, update_file, remote_location):
    """
    Sends Aleph update file to a remote location on the server to which the ssh connection is established.
    :param client: SSH client instance
    :param update_file: file we want to upload to a remote location
    :param remote_location: path to a remote location on the server to which we are connected via SSH
    :return: None
    """

    # open sftp connection
    sftp = client.open_sftp()
    # changes directory
    sftp.chdir(remote_location)
    # putting file to the remote dir
    sftp.put(update_file)
    # closing connection
    sftp.close()

    return None
