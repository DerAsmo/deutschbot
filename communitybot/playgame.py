import itertools
import time
import uuid
import discord

from communitybot.settings import HOOKS
from communitybot.embeds import Webhook

from steem.commit import Commit

class Game:

    def __init__(self, steemd_instance, bot_account):
        self.s = steemd_instance
        self.commit = Commit(steemd_instance=self.s)
        self.bot_account = bot_account
        self.debug = bool(1)

    def build_permlink(self):
        return str(uuid.uuid4())

    def get_sample_comment(self, user):
        data = {'derasmo' :  'vorstellung-von-mir-und-meiner-projektidee', 'flurgx' : 're-derasmo-vorstellung-von-mir-und-meiner-projektidee-20180213t210718018z', 'kurodevs' : 're-derasmo-vorstellung-von-mir-und-meiner-projektidee-20180213t203220853z'}

        if user in data:
            return data[user]

        return bool(0)

    def get_valid_votes(self, votes, limit):
        v_votes = []
        s_votes = sorted(votes, key=lambda tmp: tmp['time'])

        if self.debug:
            for vote in s_votes:
                if self.get_sample_comment(vote['voter']) != bool(0):
                    v_votes.append(vote)
        else:
            v_votes = s_votes

        return itertools.islice(v_votes, limit)

    def post_to_webhooks(self, score):

        hook = Webhook(None)
        hook.set_author(
            name=self.bot_account,
            url="http://steemit.com/@%s" % self.bot_account,
            icon="https://img.busy.org/@%s?height=100&width=100" %
                 self.bot_account,
        )

        hook.add_field(
            name="Message",
            value=score,
        )

        for hook_url in HOOKS:
            hook.url = hook_url
            hook.post()

    def post(self, title, body, author, permlink=None, reply_identifier=None, beneficiaries=None):
        if self.debug:
            permlink = self.get_sample_comment(author)
            print('---')
            print('Called post but post will not be submitted')
            print('Function was called with %(auth)s as author and %(ttl)s as the title' % {'auth': author, 'ttl': title})
            print('A permlink was created: %(link)s' % {'link': permlink})
            print('The posts content:')
            print(body)

        elif permlink is not None:
            self.commit.post(title, body, author, permlink, reply_identifier)
        else:
            permlink = self.build_permlink()
            self.commit.post(title, body, author, permlink, reply_identifier)

        return permlink;

    def evaluate(self, results):
        output = '<div>The game has finished. Voting results are:</div>'

        for voter, result in results.items():
            oLine = '<div>' + voter + ': ' + str(result) + '</div>'
            output = output + oLine

        thanks = '<div>Thanks for participating. If you want to support me in this project please consider voting on this comment.</div>'
        output = output + thanks

        return output

    def start_game(self):

        self.post_to_webhooks('A game has started!')

        #settings
        duration_hours = 0
        duration_minutes = 0
        duration_seconds = 5

        limit = 2

        # 1. create post
        title = 'testing a bot'
        body = 'This post is auto generated and ment for testing pupose. You can read in more detail what it\'s all about in the [introdutction post](https://steemit.com/@derasmo/vorstellung-von-mir-und-meiner-projektidee). All rewards go to @deutschbot, because I use his code, @markus.light, because he volunteered, and @reeceypie, because @ocd resteemed a post I liked.'

        permlink = 'testing-a-bot-bot-bot'

        beneficiaries = [
            {'account': '@deutschbot', 'weight': 2500},
            {'account': '@markus.light', 'weight': 3750},
            {'account': '@reeceypie', 'weight': 3750}
        ]

        permlink = self.post(title, body, self.bot_account, permlink=permlink, beneficiaries=beneficiaries)

        # 2. catch upvotes and create comments
        postid = "@" + self.bot_account + "/" + permlink;
        start = time.time()
        duration = duration_hours * 360 + duration_minutes * 60 + duration_seconds

        voters = []
        permlinks ={}

        while time.time() < start + duration:
            if len(voters) < limit :
                votes = self.s.get_active_votes(self.bot_account, permlink)

                if len(votes) > 0 :
                    # sort votes by time and cut off above limit
                    v_votes = self.get_valid_votes(votes, limit)

                    for vote in v_votes:
                        if vote['voter'] not in voters:

                            if len(voters) < 1:
                                comment_body = vote['voter'] + 'is collecting for @mack-bot. In Addition to the users mentioned in the post @mack-bot will receive a share. Please vote if you want them to win.'
                                comment_beneficiaries = [
                                                            {'account': '@deutschbot', 'weight': 2500},
                                                            {'account': '@markus.light', 'weight': 2500},
                                                            {'account': '@reeceypie', 'weight': 2500},
                                                            {'account': '@mack-bot', 'weight': 2500}
                                                        ]
                            else:
                                comment_beneficiaries = [
                                                            {'account': '@deutschbot', 'weight': 2500},
                                                            {'account': '@markus.light', 'weight': 2500},
                                                            {'account': '@reeceypie', 'weight': 2500},
                                                            {'account': '@spaminator', 'weight': 2500}
                                                        ]
                                comment_body = '@' + vote['voter'] + 'is collecting for @spaminator. In Addition to the users mentioned in the post @spaminator will receive a share. Please vote if you want them to win.'

                            if self.debug and self.get_sample_comment(vote['voter']) != bool(0):
                                self.post_to_webhooks( vote['voter'] + ' joined the game.')
                                voters.append(vote['voter'])
                                permlinks[vote['voter']] = self.post('', comment_body, vote['voter'], reply_identifier=postid, beneficiaries=comment_beneficiaries)
                            elif self.debug == bool(0):
                                self.post_to_webhooks( vote['voter'] + ' joined the game.')
                                voters.append(vote['voter'])
                                permlink = 'testing-a-bot-bot-bot-comment-' + len(voters)
                                permlinks[vote['voter']] = self.post('', comment_body, self.bot_account, reply_identifier=postid, beneficiaries=comment_beneficiaries)

            time.sleep(5)

        # 3. post summary
        results = {}
        for voter in voters:
            if self.debug:
                votes = self.s.get_active_votes(voter, permlinks[voter])
            else:
                votes = self.s.get_active_votes(self.bot_account, permlinks[voter])

            results[voter] = len(votes)

        results_body = self.evaluate(results)
        self.post_to_webhooks(results_body)
        self.post('', results_body, self.bot_account, reply_identifier=postid)