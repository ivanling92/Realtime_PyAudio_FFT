import argparse
from src.stream_analyzer import Stream_Analyzer
import time
import serial

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=None, dest='device',
                        help='pyaudio (portaudio) device index')
    parser.add_argument('--height', type=int, default=450, dest='height',
                        help='height, in pixels, of the visualizer window')
    parser.add_argument('--n_frequency_bins', type=int, default=400, dest='frequency_bins',
                        help='The FFT features are grouped in bins')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--window_ratio', default='24/9', dest='window_ratio',
                        help='float ratio of the visualizer window. e.g. 24/9')
    parser.add_argument('--sleep_between_frames', dest='sleep_between_frames', action='store_true',
                        help='when true process sleeps between frames to reduce CPU usage (recommended for low update rates)')
    return parser.parse_args()

def convert_window_ratio(window_ratio):
    if '/' in window_ratio:
        dividend, divisor = window_ratio.split('/')
        try:
            float_ratio = float(dividend) / float(divisor)
        except:
            raise ValueError('window_ratio should be in the format: float/float')
        return float_ratio
    raise ValueError('window_ratio should be in the format: float/float')

def run_FFT_analyzer():
    args = parse_args()
    window_ratio = convert_window_ratio(args.window_ratio)

    ear = Stream_Analyzer(
                    device = args.device,        # Pyaudio (portaudio) device index, defaults to first mic input
                    rate   = None,               # Audio samplerate, None uses the default source settings
                    FFT_window_size_ms  = 60,    # Window size used for the FFT transform
                    updates_per_second  = 1000,  # How often to read the audio stream for new data
                    smoothing_length_ms = 50,    # Apply some temporal smoothing to reduce noisy features
                    n_frequency_bins = args.frequency_bins, # The FFT features are grouped in bins
                    visualize = 1,               # Visualize the FFT features with PyGame
                    verbose   = args.verbose,    # Print running statistics (latency, fps, ...)
                    height    = args.height,     # Height, in pixels, of the visualizer window,
                    window_ratio = window_ratio  # Float ratio of the visualizer window. e.g. 24/9
                    )

    fps = 60  #How often to update the FFT features + display
    last_update = time.time()
    #initialize serial port
    ser = serial.Serial('COM7', 9600)
    
    #write funtion to average an array
    def average(array):
        sum = 0
        for i in range(len(array)):
            sum += array[i]
        return sum/len(array)


    while True:
        count = 0
        LOW_POINT = 0
        MED_POINT = 0
        HIGH_POINT = 0
        lave = [0]*30
        mave = [0]*30
        have = [0]*30
        if (time.time() - last_update) > (1./fps):
            last_update = time.time()
            raw_fftx, raw_fft, binned_fftx, binned_fft = ear.get_audio_features()
            low = binned_fft[0:50]
            med = binned_fft[200:250]
            high = binned_fft[350:400]
            if(count < 5):
                lave[count] = int(average(low)*100)
                mave[count] = int(average(med)*100)
                have[count] = int(average(high)*100)
                count+= 1
            else:
                LOW_POINT = average(lave)
                MED_POINT = average(mave)
                HIGH_POINT = average(have)
                count = 0
            D_LOW = int(average(low)*100)-LOW_POINT
            D_MED = int(average(med)*100)-MED_POINT
            D_HIGH = int(average(high)*100)-HIGH_POINT

           #if int(average(low)*100)> LOW_POINT:
           #    D_LOW = 1
           #else:
           #    D_LOW = 0
           #if int(average(med)*100)> MED_POINT:
           #    D_MED = 1
           #else:
           #    D_MED = 0
           #if int(average(high)*100)> HIGH_POINT:
           #    D_HIGH = 1
           #else:
           #    D_HIGH = 0

            if D_LOW > 10:
               D_LOW = b'1'
            else:
               D_LOW = b'0'
            if D_MED > 10:
                D_MED = b'1'
            else:
                D_MED = b'0'
            if D_HIGH > 10:
                D_HIGH = b'1'
            else:
                D_HIGH = b'0'
            
                
            data = str(D_LOW) + str(D_MED) + str(D_HIGH)
            print(str(D_LOW) + " " + str(D_MED) + " " + str(D_HIGH))
            ser.write(D_LOW)
            ser.write(D_MED)
            ser.write(D_HIGH)

            
        elif args.sleep_between_frames:
            time.sleep(((1./fps)-(time.time()-last_update)) * 0.99)

if __name__ == '__main__':
    run_FFT_analyzer()
