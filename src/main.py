import curses
from math import ceil

from confluent_kafka.admin import AdminClient, ConfigResource, ConfigSource
from confluent_kafka.cimpl import KafkaException
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server", action='store_true', required=False, help="Server host:port", default="localhost:9092")
args = vars(ap.parse_args())

c=AdminClient({"bootstrap.servers":args['server']})

def print_config(config, depth):
    print('%40s = %-50s  [%s,is:read-only=%r,default=%r,sensitive=%r,synonym=%r,synonyms=%s]' %
          ((' ' * depth) + config.name, config.value, ConfigSource(config.source),
           config.is_read_only, config.is_default,
           config.is_sensitive, config.is_synonym,
           ["%s:%s" % (x.name, ConfigSource(x.source))
            for x in iter(config.synonyms.values())]))

def describe_configs(a, topicName):
    """ describe configs """
    resources = [ConfigResource('topic', topicName)]

    fs = a.describe_configs(resources)

    # Wait for operation to finish.
    for res, f in fs.items():
        try:
            configs = f.result()
            for config in iter(configs.values()):
                print_config(config, 1)

        except KafkaException as e:
            print("Failed to describe {}: {}".format(res, e))
        except Exception:
            raise
topics = []
response = c.list_topics()
for topic in response.topics:
    topicMeta = response.topics[topic]
    topics.append(topic)
    print("topic : %s [%s partitions]" % (topic, len(topicMeta.partitions)))

    describe_configs(c, topic)


screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
screen.keypad( 1 )
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_BLUE)
highlightText = curses.color_pair( 1 )
normalText = curses.A_NORMAL
screen.border( 0 )
curses.curs_set( 0 )
max_row = 10 #max number of rows
box = curses.newwin( max_row + 2, 64, 1, 1 )
box.box()


row_num = len(topics)

pages = int( ceil( row_num / max_row ) )
position = 1
page = 1
for i in range( 1, max_row + 1 ):
    if row_num == 0:
        box.addstr( 1, 1, "There aren't any topic", highlightText )
    else:
        if (i == position):
            box.addstr(i, 2, str(i) + " - " + topics[i - 1], highlightText)
        else:
            box.addstr(i, 2, str(i) + " - " + topics[i - 1], normalText)
        if i == row_num:
            break

screen.refresh()
box.refresh()

x = screen.getch()
while x != 27:
    if x == curses.KEY_DOWN:
        if page == 1:
            if position < i:
                position = position + 1
            else:
                if pages > 1:
                    page = page + 1
                    position = 1 + ( max_row * ( page - 1 ) )
        elif page == pages:
            if position < row_num:
                position = position + 1
        else:
            if position < max_row + ( max_row * ( page - 1 ) ):
                position = position + 1
            else:
                page = page + 1
                position = 1 + ( max_row * ( page - 1 ) )
    if x == curses.KEY_UP:
        if page == 1:
            if position > 1:
                position = position - 1
        else:
            if position > ( 1 + ( max_row * ( page - 1 ) ) ):
                position = position - 1
            else:
                page = page - 1
                position = max_row + ( max_row * ( page - 1 ) )
    if x == curses.KEY_LEFT:
        if page > 1:
            page = page - 1
            position = 1 + ( max_row * ( page - 1 ) )

    if x == curses.KEY_RIGHT:
        if page < pages:
            page = page + 1
            position = ( 1 + ( max_row * ( page - 1 ) ) )
    if x == ord( "\n" ) and row_num != 0:
        screen.erase()
        screen.border( 0 )
        screen.addstr(14, 3, "YOU HAVE PRESSED '" + topics[position - 1] + "' ON POSITION " + str(position))

    box.erase()
    screen.border( 0 )
    box.border( 0 )

    for i in range( 1 + ( max_row * ( page - 1 ) ), max_row + 1 + ( max_row * ( page - 1 ) ) ):
        if row_num == 0:
            box.addstr( 1, 1, "There aren't strings",  highlightText )
        else:
            if ( i + ( max_row * ( page - 1 ) ) == position + ( max_row * ( page - 1 ) ) ):
                box.addstr(i - ( max_row * ( page - 1 ) ), 2, str( i ) + " - " + topics[i - 1], highlightText)
            else:
                box.addstr(i - ( max_row * ( page - 1 ) ), 2, str( i ) + " - " + topics[i - 1], normalText)
            if i == row_num:
                break



    screen.refresh()
    box.refresh()
    x = screen.getch()

curses.endwin()
exit()