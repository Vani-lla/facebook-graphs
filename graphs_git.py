import json
import matplotlib.pyplot as plt

from glob import glob
from os import listdir

from pandas import date_range
from datetime import datetime


all_conversations = []
for folder_path in listdir('./files/ff5/messages/inbox'):
    with open(f'./files/ff5/messages/inbox/{folder_path}/message_1.json', 'r') as file:
        data = json.load(file)
        participants = list([participant['name'].encode('latin1').decode('utf-8')
                             for participant in data['participants']])

    if len(participants) == 2:
        conversation = []

        for path in glob(f'./files/ff5/messages/inbox/{folder_path}/message_*.json'):
            with open(path, 'r') as file:
                data = json.load(file)

                for message in data['messages']:
                    if not ('photos' in message or 'videos' in message):

                        try:
                            conversation.append((
                                datetime.fromtimestamp(message['timestamp_ms']//1000).strftime('%Y-%m-%d'), participants.index(
                                    message['sender_name'].encode('latin1').decode('utf-8'))
                            ))
                        except:
                            pass

        conversation = sorted(conversation, key=lambda msg: msg[0])
        if conversation:
            all_conversations.append((participants[0], conversation))


def graph_values(l: list, n: int) -> list:
    values = []

    for i in range(len(l) - n):
        values.append(sum([x for x in l[i:i+n]])//n)

    # for i in range(n, 0, -1):
    #     values.append(sum([x for x in l[-i-n:-i]])//n)

    for i in range(n, 0, -1):
        values.append(sum([x for x in l[-i-1:-1]])//i)

    return values


n = 20

stats = {}
stats_count = {}
stats_seg = {}

aa = {}

margin = 1

# for person, convo in sorted(all_conversations, key=lambda convo: len(convo[1]))[::-1]:
#     print(person)

whitelist = set()
# whitelist.add("John Doe")

# f_date = min(filter(lambda convo: convo[0] in whitelist, all_conversations), key=lambda convo: convo[1][0][0])[1][0][0]
# l_date = max(filter(lambda convo: convo[0] in whitelist, all_conversations), key=lambda convo: convo[1][-1][0])[1][-1][0]

f_date = min(all_conversations, key=lambda convo: convo[1][0][0])[1][0][0]
l_date = max(all_conversations, key=lambda convo: convo[1][-1][0])[1][-1][0]
all_dates = date_range(f_date, l_date, freq='d')

n_o_people = -1

if len(whitelist) == 0:
    data_set = sorted(all_conversations,
                      key=lambda convo: len(convo[1]))[:-n_o_people:-1]
else:
    data_set = filter(lambda x: x[0] in whitelist, sorted(
        all_conversations, key=lambda convo: len(convo[1]))[:15:-1])


for person, conversation in data_set:

    # if person in whitelist:
    days = {}
    days_seg = {}
    days_total = {}
    values3 = []

    for date in all_dates:
        days[datetime.strftime(date, '%Y-%m-%d')] = 0
        days_seg[datetime.strftime(date, '%Y-%m-%d')] = [0, 0]
    days[f_date] = 0

    for day, sender in conversation:
        days[day] += 1
        days_seg[day][sender] += 1*.9

    cl = list(days.items())
    t = 0

    for ind, element in enumerate(cl[1:]):
        key = element[0]
        value = element[1]
        t += value

        if value == 0:
            days_total[key] = t
        else:
            days_total[key] = t + value

    cl = list(days_seg.items())
    t0 = 0
    t1 = 0
    tt = 1

    for _, pair in cl:
        s = sum(pair)
        t0 += pair[0]
        t1 += pair[1]
        tt += s

        # if s == 0:
        #     values3.append(t0/tt)
        # else:
        values3.append(t1/tt)

    stats[person] = days
    stats_count[person] = days_total
    stats_seg[person] = values3
    aa[person] = days_seg

fig, axs = plt.subplots(4)

g_total = {}
g_total_k = {}

t = 0
t1 = 0

for date in all_dates:
    for person in stats:
        t += stats[person][datetime.strftime(date, '%Y-%m-%d')]

    g_total[datetime.strftime(date, '%Y-%m-%d')] = t
    g_total_k[datetime.strftime(date, '%Y-%m-%d')] = t1

received = []
sent = []

r, s = 0, 0

for date in all_dates:
    for person in stats:
        r += aa[person][datetime.strftime(date, '%Y-%m-%d')][0]
        s += aa[person][datetime.strftime(date, '%Y-%m-%d')][1]

    received.append(r)
    sent.append(s)

names, _ = zip(*stats[person].items())

fig.suptitle("Wykresy ważności")


axs[3].plot(names, received, label="Received")
axs[3].plot(names, sent, label="Sent")

print('done with data')
for person in stats:
    _, values = zip(*stats[person].items())
    names2, values2 = zip(*stats_count[person].items())
    values3 = stats_seg[person]

    axs[0].plot(names, graph_values(values, n), label=person)
    axs[0].set_title('Wiadomości na dzień')

    axs[1].plot(names2, values2, label=person)
    axs[1].set_title('Wiadomości łącznie')

    axs[2].plot(names, values3, label=person)
    axs[2].set_title('Magiczny wskaźnik przyjaźni')
    axs[2].set_ylim([.3, .7])

    axs[2].plot(names, values3, label=person)
    axs[2].set_title('Magiczny wskaźnik przyjaźni')
    axs[2].set_ylim([.3, .7])

plt.legend()
plt.show()
