import vlc


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
