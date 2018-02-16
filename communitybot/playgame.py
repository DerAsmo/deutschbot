import itertools
import time
import uuid

from steem.commit import Commit

class Game:

    def __init__(self, steemd_instance, bot_account):
        self.s = steemd_instance
        self.commit = Commit(steemd_instance=self.s)
        self.bot_account = bot_account
        self.debug = bool(1)

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

    def build_permlink(self):
        return str(uuid.uuid4())

    def post(self, title, body, author, reply_identifier=None):
        if self.debug:
            permlink = self.get_sample_comment(author)
        else:
            permlink = self.build_permlink()
            self.commit.post(title, body, author, permlink, reply_identifier)

        return permlink;

    def evaluate(self, results):
        output = ''

        for voter, result in results.items():
            oLine = '<div>' + voter + ': ' + str(result) + '</div>'
            print(oLine)
            output = output + oLine

        return output

    def start_game(self):

        # 1. create post
        title = 'test title'
        body = 'test body'
        permlink = self.post(title, body, self.bot_account)

        # 2. catch upvotes and create comments
        postid = "@" + self.bot_account + "/" + permlink;
        start = time.time()
        hours = 0
        minutes = 0
        seconds = 15
        duration = hours * 360 + minutes * 60 + seconds
        
        limit = 2;
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

                            if self.debug and self.get_sample_comment(vote['voter']) != bool(0):
                                voters.append(vote['voter'])
                                permlinks[vote['voter']] = self.post('', body, vote['voter'], postid)
                            elif self.debug == bool(0):
                                voters.append(vote['voter'])
                                permlinks[vote['voter']] = self.post('', body, self.bot_account, postid)

            time.sleep(5)

        # 3. post summary
        results = {}
        for voter in voters:
            if self.debug:
                votes = self.s.get_active_votes(voter, permlinks[voter])
            else:
                votes = self.s.get_active_votes(self.bot_account, permlinks[voter])

            results[voter] = len(votes)

        bodyResult = self.evaluate(results)
        self.post('', bodyResult, self.bot_account, postid)