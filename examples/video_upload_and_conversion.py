from filestack import Client

client = Client('<YOUR_API_KEY')

new_video = client.upload(filepath='/PATH/TO/FILE')
new_video_conversion = new_video.av_convert(width=400, height=400)

while new_video_conversion.status != 'completed':
    print('not completed yet')

print(new_video_conversion.to_filelink().url)
