__author__ = 'cephalopodblue'
import essentia
import essentia.standard
import essentia.streaming
import math
import matplotlib.pyplot as pyplot

__show_audio = False
__sample_rate = 44100
__frames_per_second = 10
__short_frames_per_second = 1
__resample_rate = 1000
__plot_length = 60


def _load_audio(file_name):
    loader = essentia.standard.MonoLoader(filename=file_name)
    audio = loader()
    return audio


def find_data(file_name, output_file=False, plotting=False):
    #find data
    audio = _load_audio(file_name)
    pool = essentia.Pool()

    _find_power(audio, pool)

    if plotting is False:
        _find_data(audio, pool)
        if output_file is not False:
            essentia.standard.YamlOutput(filename = output_file, format='json')(pool)
        elif plotting is False:
            essentia.standard.YamlOutput(format='json')(pool)
    else:
        _plot(pool)


def _find_data(audio, pool):
    rhythm = essentia.standard.RhythmExtractor2013()
    fade_detection = essentia.standard.FadeDetection()
    replay_gain = essentia.standard.ReplayGain()
    danceability = essentia.standard.Danceability()
    dynamic_complexity = essentia.standard.DynamicComplexity()
    level_extractor = essentia.standard.LevelExtractor()
    tonal_extractor = essentia.standard.TonalExtractor()

    tonal_info = tonal_extractor(audio)
    pool.add("Chords Changes Rate", tonal_info[0])
    pool.add("Chords Histogram", tonal_info[1])
    pool.add("Chords Key", tonal_info[2])
    pool.add("Chords Number Rate", tonal_info[3])
    pool.add("Chord Progression", tonal_info[4])
    pool.add("Chord Scale", tonal_info[5])
    pool.add("Chord strength", tonal_info[6])
    pool.add("HPCP", tonal_info[7])
    pool.add("High Res HPCP", tonal_info[8])
    pool.add("Key", tonal_info[9])
    pool.add("Scale", tonal_info[10])
    pool.add("Key Strength", tonal_info[11])

    pool.add("Replay Gain", replay_gain(audio))
    pool.add("Danceability", danceability(audio))
    pool.add("Dynamic Complexity", dynamic_complexity(audio))
    pool.add("Loudness", level_extractor(audio))

    fade = fade_detection(audio)
    pool.add("Fade In", fade[0])
    pool.add("Fade Out", fade[1])

    rhythm_descriptors = rhythm(audio)
    pool.add("BPM", rhythm_descriptors[0])
    pool.add("BPM Ticks", rhythm_descriptors[1])
    pool.add("BPM Confidence", rhythm_descriptors[2])
    pool.add("BPM Estimates", rhythm_descriptors[3])
    pool.add("BPM Intervals", rhythm_descriptors[4])

    return pool


def _find_power(audio, pool):
    #Calculate average power at specified & one-second intervals
    frame_size = __sample_rate / __frames_per_second
    instant_power = essentia.standard.InstantPower()

    average_power = instant_power(audio)
    pool.add('average_power', average_power)

    #Calculate power averages for specified intervals
    num = 1
    below_average = 0
    above_average = 0
    max_power = 0
    std_dev = 0
    for frame in essentia.standard.FrameGenerator(audio, frameSize=frame_size, hopSize=frame_size):
        power = instant_power(frame)

        if power < average_power:
            below_average += 1
        else:
            above_average += 1
            if power > max_power:
                max_power = power

        std_dev += (power - average_power) * (power - average_power)

        pool.add('power', power)
        pool.add('power_time', num * (__resample_rate / __frames_per_second))
        num += 1

    #Calculate power averages for one-second intervals
    num = 1
    for frame in essentia.standard.FrameGenerator(audio, frameSize=__sample_rate, hopSize=__sample_rate):
        short_power = instant_power(frame)

        pool.add('short_power', short_power)
        pool.add('short_power_time', num * __resample_rate)
        num += 1

    pool.add('percent_below_average', below_average / float(pool['power_time'].size))
    pool.add('percent_above_average', above_average / float(pool['power_time'].size))
    pool.add('max_power', max_power)
    pool.add('standard_deviation', math.sqrt(std_dev / pool['power'].size))

    return pool


def _plot(pool):
    #if plotting, plot (the plot option will ONLY calculate values needed for plotting)
    #and will not print to a file even if one is provided
    ax = pyplot.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_position(('data', 0))

    pyplot.ylim(0, pool['max_power'])
    pyplot.plot(pool['power_time'], pool['power'], color='pink', label='1/10-Sec Power')
    pyplot.plot(pool['short_power_time'], pool['short_power'], color='blue', label="1-sec Power")

    pyplot.axhline(pool['average_power'], color='black', label='Average Power')
    pyplot.axhline(pool['average_power'] - pool['standard_deviation'], color='red', label='Standard Deviation')
    pyplot.axhline(pool['average_power'] + pool['standard_deviation'], color='red', label='Standard Deviation')
    pyplot.annotate('Average Power:\n' + str(pool['average_power']),
                    xy=(0, pool['average_power']), xytext=(1000, pool['average_power']))

    pyplot.show()
