﻿#include "VideoStream.hpp"

int main(int argc, char *argv[])
{
    VideoStream stream("My video stream");

    try 
    {
        stream.SetPipeline("v4l2src device=/dev/video0 ! videoconvert ! autovideosink");
        stream.ListenOn("127.0.0.1", 8080);

        while (stream.IsListening()) 
        {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
    }
    catch (const std::exception& e)
    {
        Log::Get().Critical(e.what());
    }

    return 0;
}
