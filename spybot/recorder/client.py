from django.utils import timezone

from spybot.models import TSID, TSUser, TSUserActivity, TSChannel


class Client:

    """
    called when a client enters
    """
    def client_enter(self, client_id: int, channel_id: int, client_database_id: int, client_nickname: str,
                     client_type: int, client_unique_identifier: str):
        # TODO save bots maybe
        if client_type == "1":
            # because fuck that tsmonitor
            return

        # check if we have this user yet
        tsid, tsuser = None, None
        try:
            tsid = TSID.objects.get(ts_id=client_unique_identifier)
            tsuser = tsid.tsuser
            assert tsuser.id
            # user exists

            # update nickname in DB if the user changed it
            if tsuser.name != client_nickname:
                print("User changed their name")
                tsuser.name = client_nickname
                tsuser.save()

            print(f"found existing TSID for user: {tsuser.name} with id={tsid}")
            self.__client_start_session(tsuser, channel_id, client_id, joined=True)

        except TSID.DoesNotExist as e:
            print(f"did not find TSID for user {e}")
            # create new TSUser and TSID for this client
            u = TSUser(name=client_nickname, client_id=client_id)
            u.save()
            tsid = TSID(tsuser_id=u.id, ts_id=client_unique_identifier)
            tsid.save()
            self.__client_start_session(u, channel_id, client_id, joined=True)
            print(f"created tsuser {u.name} and tsid {u.id}for new client")

        # enter new client into DB

    # called on user disconnect
    # client_id: userID
    # channel_id: channel that was left
    # reason_id: 3 for timeout, 0 for intended disconnect, 8 unknown
    def client_leave(self, client_id: int, channel_id: int, reason_id: int = -1):
        try:
            user = TSUser.objects.get(client_id=client_id)
            user.client_id = 0
            user.online = False
            user.save()

            self.__client_end_session(user, reason_id)
        except TSUser.DoesNotExist as e:
            print(f"caught a bot leaving: {e}")

    def client_move(self, client_id: int, channel_to_id: int, reason_id: int):
        print("Client moved!")
        user = self.__get_user_from_client_id(client_id)

        self.__client_end_session(user, reason_id)
        self.__client_start_session(user, channel_to_id, client_id, joined=False)

    def __client_start_session(self, ts_user: TSUser, channel_id: int, client_id: int, joined):
        ts_user.client_id = client_id
        ts_user.online = True
        ts_user.save()

        try:
            channel = TSChannel.objects.get(id__exact=channel_id)
            new_activity = TSUserActivity(tsuser=ts_user, start_time=timezone.now(),
                                          channel=channel, joined=joined)
            new_activity.save()
        except TSChannel.DoesNotExist as e:
            print(f"channel ID wrong: {channel_id}")

    def __client_end_session(self, ts_user: TSUser, reason_id: int):
        # old_activity = newest TSUserActivity for client_id (in channel_id)
        # insert endTime, reason_id into old_activity
        try:
            old_activity = TSUserActivity.objects.order_by('-start_time').filter(tsuser=ts_user)[0]

            if old_activity.end_time is not None:
                raise ValueError('end_time should be empty here')

            old_activity.end_time = timezone.now()
            old_activity.disconnect_id = reason_id
            old_activity.save()
        except Exception as e:  # TODO specify Exception
            print(f"User does not exist or smth: {e}")

    def __get_user_from_client_id(self, client_id: int):
        try:
            ts_user = TSUser.objects.get(client_id__exact=client_id)
            return ts_user
        except TSUser.DoesNotExist as e:
            print(f"Error client ID is wrong: {e}")

    """
    make sure session is correct and correct if mistakes were made
    if user is already online, check if he has an open session
    if so, make sure it is for the correct channel
    if no close it and start a new one
    TODO maybe even remove it
    """
    def handle_old_sessions(self, clients):

        # get all open sessions and close them
        open_sessions = TSUserActivity.objects.filter(end_time=None)

        for session in open_sessions:

            keep_session_user = None

            for client in clients:
                if session.tsuser.client_id == int(client['clid']) \
                        and session.channel.id == int(client['cid']):
                    # KEEP SESSION OPEN
                    keep_session_user = client
                    break

            if keep_session_user:
                print(f"Keeping old session alive probably for {session.tsuser.name}")
                clients.remove(keep_session_user)
            elif not keep_session_user:
                print("Ending old session")
                self.__client_end_session(session.tsuser, -2)

        return clients
