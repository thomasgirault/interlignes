import numpy as np
from sklearn.neighbors import NearestNeighbors

# https://github.com/opencv/opencv_contrib/blob/master/modules/tracking/samples/multitracker.py
# https://stackoverflow.com/questions/26363257/tracking-multiple-moving-objects-with-kalmanfilter-in-opencv-c-how-to-assign


class MultiObjectTracker:

    # We only care about trackers who have been alive for the given lifetimeThreshold number of frames.
    lifetimeThreshold = 20
    # We won't associate a tracker with a mass center if the distance
    # between the two is greater than this fraction of the frame dimension
    # (taken as average between width and height).
    distanceThreshold = 10
    distanceMovingThreshold = 5
    
    # Kill a tracker if it has gone missedFramesThreshold frames without receiving a measurement.
    # Tracks are terminated if they are not detected for TLost frames.
    missedFramesThreshold = 10


    # Delta time, used to set up matrices for Kalman trackers.
    dt = 0.2  # Delta time, used to set up matrices for Kalman trackers.
    # Magnitude of acceleration noise. Used to set up Kalman trackers.
    magnitudeOfAccelerationNoise = 0.5

    def __init__(self, nb_tracked=100):
        self.tracked = np.zeros((nb_tracked, 2))
        self.tracked.fill(-self.distanceThreshold)
        self.missed_frames = nb_tracked * [0]
        self.knn = NearestNeighbors(
            n_neighbors=1, algorithm='brute', metric='euclidean')
        self.knn.fit(self.tracked)


    def hungarian(self, mass_centers, bounding_rects):
        """
        1 - calculer la matrice D des distances entre pos_i et pos_i+1
        2 - transformer D en matrice carrée
        3 - appliquer l'algorithme hongrois (asgn, cost)=OPTASIGN(D)
        4 - rejeter les distances plus élévées qu'un seuil fixé

        https://www.youtube.com/watch?v=HQW4wtLBddk&t=384


        'tracklets'

        SORT https://arxiv.org/pdf/1602.00763.pdf
        x = [cx, cy, s, r, cx',cy',s']T
        cx, cy : coordonnées du centre
        s : scale (aire)
        r : ratio

        If no detection is associated to the target,
        its state is simply predicted without correction using the
        linear velocity model.

        IOU : Intersection over Union distance between each detection and all predicted bounding boxes from the existing targets        
        """
        
        pass


    def update(self, rects):
        """Update the object tracker with the mass centers of the observed boundings rects."""
        tracking_outputs = None

        mass_centers = np.array([(rects[0] + rects[2]) /2., (rects[1] + rects[3]) /2.]) 
        # mass_centers = (int((x + w) / 2), int((y + h) / 2))

        # le point peut inclure
        # - la couleur normalisée des mass_centers ?
        # - la vitesse précédemment calculée pour ce point
        # if True:
        #     yield ("1",[0,0])
        #     return
        if len(mass_centers) == 0:
            return
        #     return self.tracked

        dist, indices = self.knn.kneighbors(mass_centers)
        sort_dist = np.argsort(dist, axis=0)

        points = []

        # prendre en compte le temps
        assigned = np.argwhere(self.tracked[:, 0] != -10).T.tolist()[0]
        unassigned = np.argwhere(self.tracked[:, 0] == -10).T.tolist()[0]

        for idx in sort_dist:
            idx = idx[0]
            nearest_last_idx = indices[idx][0]
            d = dist[idx][0]
            # print(idx, nearest_last_idx, d)

            # si le point à déjà été assigné ou qu'il est trop loin des autres
            # c'est un nouveau point
            if nearest_last_idx in points or d > self.distanceThreshold:
                nearest_last_idx = unassigned.pop(0)
                print("TRACK new walker", nearest_last_idx)
                # else: # c'est un point connu
            points.append(nearest_last_idx)
            self.missed_frames[nearest_last_idx] = 0
            self.tracked[nearest_last_idx] = mass_centers[idx]
            if d < self.distanceMovingThreshold:
                yield (str(nearest_last_idx), self.tracked[nearest_last_idx].tolist())

        # Ré-init old points
        reinit_index = set(assigned) - set(points)
        for idx in reinit_index:
            if self.missed_frames[idx] > self.missedFramesThreshold:
                print("UNTRACK Walker", idx)
                self.tracked[idx] = - self.distanceThreshold
                self.missed_frames[idx] = 0
            else:
                # yield (idx, self.tracked[idx])
                self.missed_frames[idx] += 1

        self.knn.fit(self.tracked)

        # maintenir la liste des assignés et bon assignés

        # return self.tracked
        # points.append(mass_centers[updated_index])
        # return points
        # new_points = []
        # remove_points = []
        # keep_point = []
        # seen_points = []
        # points.append(nearest_last_idx)
        # self.tracked[nearest_last_idx] = mass_centers[idx]
        # currentFrameC is the same object as lastFrameC so give it the same ID
        # print(dist)
        # print(indices)
        # print(unassigned)
        # print(sort_dist)

        # if distance(currentFrameC, lastFrameC) is smallest and < threshold
        # Pour un point P,
        # si aucun nouveau point associé n'est son plus proche voisin
        #    et que le delay et passé
        # on réinitialise le point
        # if "lost_tracking": # delay lost
        #   self.tracked[idx] = -10

        # points[pos] = idx

        # print(points)
        # if no shortest contour with dist < thres was found, create a new object with a new ID and create a new KalmanFilter with this same ID for that object

        # for each contour 'currentFrameC':
        #     for each contour 'lastFrameC'

        # call kalmanFilter with ID for each found contour ID

        # for d, idx in zip(distances, indices):
        # self.knn.fit(mass_centers)
        # on assigne d'abors les plus proches à des points connus

        # return dist, indices

        # if "Track One" == True:
        #     updated_index = sort_dist[0][0]
        #     self.tracked = np.array([mass_centers[updated_index]])
        #     return self.tracked


if __name__ == '__main__':
    import time
    X = np.array([[2, 3], [0.1, 2.5], [1.8, 3], [3, 1.1], [1.1, 0.9]])
    X2 = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])

    t0 = time.time()
    mot = MultiObjectTracker()

    print(list(mot.update(X, None)))

    print(list(mot.update(X2, None)))
    # sorted = np.argsort(d, axis=0)
    t1 = time.time()

    print((t1 - t0) * 1000, "ms")

    # from sklearn.metrics.pairwise import euclidean_distances
    # from scipy.optimize import linear_sum_assignment
    # X2 = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])

    # d = euclidean_distances(X2, X)
    # print(d)

    # row_ind, col_ind = linear_sum_assignment(1 - d)
    # print(row_ind, col_ind)

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
