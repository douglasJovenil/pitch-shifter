import aubio
from aubio import tempo, source
from src.settings import Path


def main():
  transpose = 12
  samplerate = 0
  hop_size = 64
  mode = "default"
  input_file = Path.SAMPLE_WAV_FILE
  output_file = 'output.wav'

  


def pitch_shift(transpose, samplerate, hop_size, mode, input_file, output_file):
  source_read = aubio.source(input_file, samplerate, hop_size)
  if samplerate == 0: samplerate = source_read.samplerate
  sink_out = aubio.sink(output_file, samplerate)

  pitchshifter = aubio.pitchshift(mode, 1., hop_size, samplerate)
  if transpose: pitchshifter.set_transpose(transpose)

  total_frames, read = 0, hop_size
  transpose_range = 23.9
  while read:
    vec, read = source_read()
    # transpose the samples
    out = pitchshifter(vec)
    # position in the file (between 0. and 1.)
    percent_read = total_frames / float(source_read.duration)
    # variable transpose rate (in semitones)
    transpose = 2 * transpose_range * percent_read - transpose_range
    # set transpose rate
    pitchshifter.set_transpose(transpose)
    # print the transposition
    #print pitchshifter.get_transpose()
    # write the output
    sink_out(out, read)
    total_frames += read

  # end of file, print some results
  outstr = "wrote %.2fs" % (total_frames / float(samplerate))
  outstr += " (%d frames in" % total_frames
  outstr += " %d blocks" % (total_frames // source_read.hop_size)
  outstr += " at %dHz)" % source_read.samplerate
  outstr += " from " + source_read.uri
  outstr += " to " + sink_out.uri
  print(outstr)

  

if __name__ == '__main__':
  main()