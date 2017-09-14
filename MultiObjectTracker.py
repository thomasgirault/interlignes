class MultiObjectTracker:
    
    # We only care about trackers who have been alive for the given lifetimeThreshold number of frames.
    lifetimeThreshold = 20

    # We won't associate a tracker with a mass center if the distance
    # between the two is greater than this fraction of the frame dimension
    # (taken as average between width and height).
    distanceThreshold = 0.1


    # Kill a tracker if it has gone missedFramesThreshold frames without receiving a measurement.
    missedFramesThreshold = 10

    # Delta time, used to set up matrices for Kalman trackers.
    dt = 0.2 # Delta time, used to set up matrices for Kalman trackers.

    # Magnitude of acceleration noise. Used to set up Kalman trackers.
    magnitudeOfAccelerationNoise = 0.5
    

    def __init__(self):
        # The actual object trackers.
        self.tracker = []

# Check if the Kalman filter at index i has another Kalman filter that can suppress it.
# Any Kalman filter with a lifetime above this value cannot be suppressed.
# A Kalman filter can only be suppressed by another filter which is threshold * framDiagonal
# or closer.
# A Kalman filter can only be suppressed by another filter which is threshold times its age.
# Check if the tracker prediction at index i shares the given
# bounding rectangle with another point.
    # lifetimeSuppressionThreshold = 20
    # distanceSuppressionThreshold = 0.1
    # ageSuppressionThreshold = 2



    def update(self, mass_centers, bounding_rects):
        """Update the object tracker with the mass centers of the observed boundings rects."""
        tracking_outputs = None


        
  