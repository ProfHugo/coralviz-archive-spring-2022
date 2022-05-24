import argparse
import cv2
import os
import _thread
import pathlib

def main():
	# retrieve and parse arguments
	parser = argparse.ArgumentParser(description="Sample images from a MP4 video")
	parser.add_argument("sampling_interval", type=int, help="the number of frames between each sampled image")
	parser.add_argument("img_format", choices=["png", "jpeg", "jpg"], help="The format of the sampled images")
	parser.add_argument("-ql", metavar="jpeg_quality_level", required=False, default=95, type=int, help="the Quality Level of the image (JPEG only)")
	parser.add_argument("-cl", metavar="png_compression_level", required=False, default=0, type=int, help="the Compression Level of the image (PNG only)")
	parser.add_argument("-sf", metavar="start_frame", required=False, default=0, type=int, help="the frame to start at")
	parser.add_argument("-ef", metavar="end_frame", required=False, default=-1, type=int, help="the frame to end at (if negative, go through the whole video)")
	parser.add_argument("-sd", metavar="save_dir", required=False, default="out/", type=str, help="the directory to save the output images in")
	parser.add_argument("video_paths", nargs=argparse.ONE_OR_MORE, type=str)
	args = parser.parse_args()

	# create save directory if it does not exist
	if not os.path.isdir(args.sd):
		os.mkdir(args.sd)

	# go through each video
	for video_path in args.video_paths:
		sample_video(video_path, args.sampling_interval, args.img_format, args.sd, args.sf, args.ef, args.ql, args.cl)

def sample_video(video_name, sampling_interval, img_format, save_dir, start_frame, end_frame, jpeg_ql, png_cl):
	# validate input
	if not os.path.exists(video_name):
		print(f"{video_name} cannot be found")
		return
	if not video_name.lower().endswith(".mp4"):
		print(f"{video_name} is not a MP4 video")
		return
	vid = cv2.VideoCapture(video_name)
	frame_count = start_frame
	while vid.isOpened():
		retval, frame = vid.read()
		if retval:
			# image name format: <videoname>_<timecode>_RAW.ext
			match img_format:
				case "png":
					fname = f"{save_dir}{pathlib.Path(video_name).resolve().stem}_{frame_count}f_RAW.png"
					write_args = [cv2.IMWRITE_PNG_COMPRESSION, png_cl]
				case "jpg" | "jpeg":
					fname = f"{save_dir}{pathlib.Path(video_name).resolve().stem}_{frame_count}f_RAW.jpg"
					write_args = [cv2.IMWRITE_JPEG_QUALITY, jpeg_ql]
			cv2.imwrite(fname, frame, write_args)
			print(f"Saved frame {frame_count} of {video_name} to {fname}")
			# advance to the next frame by setting the video to frame_count
			frame_count += sampling_interval
			vid.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
		else:
			print(f"Sampling finished for {video_name} at frame {frame_count}")
			break
	#close the video
	vid.release()

if __name__ == "__main__":
	main()