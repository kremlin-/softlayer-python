"""Details of a specific event, and ability to acknowledge event."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers.account import AccountManager as AccountManager
from SoftLayer import utils

@click.command()
@click.argument('identifier')
@click.option('--ack', is_flag=True, default=False,
              help="Acknowledge Event. Doing so will turn off the popup in the control portal")
@environment.pass_env
def cli(env, identifier, ack):
    """Details of a specific event, and ability to acknowledge event."""

    # Print a list of all on going maintenance 
    manager = AccountManager(env.client)
    event = manager.get_event(identifier)

    if ack:
        result = manager.ack_event(identifier)

    env.fout(basic_event_table(event))
    env.fout(impacted_table(event))
    env.fout(update_table(event))

def basic_event_table(event):
    table = formatting.Table(["Id", "Status", "Type", "Start", "End"], title=event.get('subject'))

    table.add_row([
        event.get('id'),
        utils.lookup(event, 'statusCode', 'name'),
        utils.lookup(event, 'notificationOccurrenceEventType', 'keyName'),
        utils.clean_time(event.get('startDate')),
        utils.clean_time(event.get('endDate'))
    ])

    return table

def impacted_table(event):
    table = formatting.Table([
        "Type", "Id", "hostname", "privateIp", "Label"
    ])
    for item in event.get('impactedResources', []):
        table.add_row([
            item.get('resourceType'),
            item.get('resourceTableId'),
            item.get('hostname'),
            item.get('privateIp'),
            item.get('filterLabel')
        ])
    return table

def update_table(event):
    update_number = 0
    for update in event.get('updates', []):
        header = "======= Update #%s on %s =======" % (update_number, utils.clean_time(update.get('startDate')))
        click.secho(header, fg='green')
        update_number = update_number + 1
        text = update.get('contents')
        # deals with all the \r\n from the API
        click.secho("\n".join(text.splitlines()))
