import time
import uuid

from steem.commit import Commit

class Game:

    def __init__(self, steemd_instance, expected_tags, bot_account):
        self.s = steemd_instance
        self.commit = Commit(steemd_instance=self.s)
        self.bot_account = bot_account

    def build_permlink(self):
        return str(uuid.uuid4())

    def post(self, title, body, author, reply_identifier=None):
        permlink = self.build_permlink();
    
        self.commit.post(title, body, author, permlink, reply_identifier)

        return permlink;

    def start_game(selfs):

        # 1. create post
        title = "test title"
        body = "test body content"
        permlink = self.post(title, body, self.bot_account)

        # 2. catch upvotes and create comments
        postid = "@" + self.bot_account + "/" + permlink;
        start = time.time()
        hours = 24
        minutes = 0
        seconds = 0
        duration = hours * 360 + minutes * 60 + seconds
        
        limit = 2;
        voters = []
        permlinks = []

        while time.time() < start + duration:
            votes = s.get_active_votes(self.bot_account, permlink);

            if voters.count() > 0 and voters.count() < limit :
                for vote in votes:
                    if vote['voter'] not in voters:
                        voters.append(vote['voter'])
                        permlinks[vote['voter']] = self.post('', body, author, postid)
            time.sleep(10)

        # 3. post summary
        results = [];
        for key, voter in voters:
            votes = s.get_active_votes(self.bot_account, permlinks[voter])
            results[voter] = votes.count()

        bodyResult = evaluate(results)
        self.post('', bodyResult, self.bot_account, postid)