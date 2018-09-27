"""
------------------------------------------------------------------------------

The MIT License (MIT)

Copyright (c) 2018

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

------------------------------------------------------------------------------
"""
import soundcloud
import vlc
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger


class SoundCloudPlayer(object):
    def play(self, urls):
        instanceParameters = [
            '--quiet',
            '--ignore-config',
            '--sout-keep',
            '--sout-all',
            '--vout=caca'
        ]
        self.instance = vlc.Instance(instanceParameters)
        self.medialist = self.instance.media_list_new()
        # self.medialist.add_media(self.instance.media_new(url))
        for item in urls:
            self.medialist.add_media(self.instance.media_new(item))
        self.player = self.instance.media_list_player_new()
        self.player.set_media_list(self.medialist)
        self.player.play()

    def stop(self):
        self.player.stop()


# Each skill is contained within its own class, which inherits base methods
# from the MycroftSkill class.  You extend this class as shown below.

LOGGER = getLogger(__name__)


class SoundcloudSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(SoundcloudSkill, self).__init__(name="SoundcloudSkill")

        # Initialize working variables used within the skill.
        self.count = 0
        self.player = SoundCloudPlayer()

    # The "handle_xxxx_intent" function is triggered by Mycroft when the
    # skill's intent is matched.  The intent is defined by the IntentBuilder()
    # pieces, and is triggered when the user's utterance matches the pattern
    # defined by the keywords.  In this case, the match occurs when one word
    # is found from each of the files:
    #    vocab/en-us/Hello.voc
    #    vocab/en-us/World.voc
    # In this example that means it would match on utterances like:
    #   'Hello world'
    #   'Howdy you great big world'
    #   'Greetings planet earth'
    @intent_handler(IntentBuilder("").require("Play").require("Soundcloud"))
    def handle_soundcloud_intent(self, message):
        try:
            # In this case, respond by simply speaking a canned response.
            # Mycroft will randomly speak one of the lines from the file
            #    dialogs/en-us/hello.world.dialog
            utterance = message.data['utterance']
            LOGGER.info("utterance is " + utterance)
            to_word = ' ' + self.translate('To')
            on_word = ' ' + self.translate('On')
            query = to_word.join(utterance.split(to_word)[1:])
            LOGGER.info("query replace 1 is " + query)
            query = on_word.join(query.split(on_word)[1:])
            LOGGER.info("query replace 2 is " + query)
            trackName = query.strip()
            LOGGER.info("Finding some tracks for " + trackName)
            message.data['track'] = trackName
            self.play_song(message)
        except Exception as e:
            LOGGER.error("Error: {0}".format(e))

    @intent_handler(IntentBuilder("").require("Stop").require("Soundcloud"))
    def handle_soundcloud_stop_intent(self, message):
        self.stop()

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, there is no need to override it.  If you DO
    # need to implement stop, you should return True to indicate you handled
    # it.
    #
    def stop(self):
        self.player.stop()
        return True

    def play_song(self, message):
        """
        When the user wants to hear a song, optionally with artist and/or
        album information attached.
        play the song <song>
        play the song <song> by <artist>
        play the song <song> off <album>
        play <song> by <artist> off the album <album>
        etc.

        Args:
            message (Dict): The utterance as interpreted by Padatious
        """
        song = message.data.get('track')

        # create a client object with your app credentials
        client = soundcloud.Client(client_id='bK2tF3BXmEa5vVQCI1xTZTA9NSwA5NPv')

        # find all sounds
        tracks = client.get('/tracks', q=song)
        urls = []
        name = tracks[0].title
        LOGGER.info("First track to be played is " + name)
        for track in tracks:
            urls.append(client.get(tracks[0].stream_url, allow_redirects=False).url)

        self.speak_dialog("play.soundcloud", data={"track": name})
        self.player.play(urls)


# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return SoundcloudSkill()
