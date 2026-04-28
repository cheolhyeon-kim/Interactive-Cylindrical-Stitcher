import numpy as np
import cv2 as cv


def prepare_images(names, width=600):
    imgs = []
    for name in names:
        img = cv.imread(name)
        if img is None:
            print(f"Error: {name}을(를) 찾을 수 없습니다.")
            continue
        h, w = img.shape[:2]
        ratio = width / float(w)
        imgs.append(cv.resize(img, (width, int(h * ratio))))
    return imgs


def project_cylindrical(img, focal_length):
    h, w = img.shape[:2]
    result = np.zeros_like(img)
    center_x, center_y = w / 2, h / 2
    for y in range(h):
        for x in range(w):
            theta = (x - center_x) / focal_length
            h_hat = (y - center_y) / focal_length
            x_hat, y_hat, z_hat = np.sin(theta), h_hat, np.cos(theta)
            x_orig = int(focal_length * x_hat / z_hat + center_x)
            y_orig = int(focal_length * y_hat / z_hat + center_y)
            if 0 <= x_orig < w and 0 <= y_orig < h:
                result[y, x] = img[y_orig, x_orig]
    return result


def run_stitching(val):
    f = max(val, 1) 
    cyl_images = [project_cylindrical(img, f) for img in images]
    
    sift = cv.SIFT_create()
    bf = cv.BFMatcher()
    
    base_img = cyl_images[0]
    h, w = base_img.shape[:2]
    canvas = np.zeros((h * 2, w * 5, 3), dtype=np.uint8) 
    offset_y, offset_x = h // 2, 0
    canvas[offset_y:offset_y+h, offset_x:offset_x+w] = base_img
    
    H_total = np.array([[1.0, 0, offset_x], [0, 1.0, offset_y], [0, 0, 1.0]])
    
    for i in range(1, len(cyl_images)):
        kp1, des1 = sift.detectAndCompute(cyl_images[i-1], None)
        kp2, des2 = sift.detectAndCompute(cyl_images[i], None)
        
        matches = bf.knnMatch(des1, des2, k=2)
        good = [m for m, n in matches if m.distance < 0.75 * n.distance]
        
        if len(good) < 4: continue
        
        pts1 = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
        
        H_step, _ = cv.findHomography(pts2, pts1, cv.RANSAC, 5.0)
        H_total = np.matmul(H_total, H_step)
        
        warped = cv.warpPerspective(cyl_images[i], H_total, (canvas.shape[1], canvas.shape[0]))
        
        mask_warped = (cv.cvtColor(warped, cv.COLOR_BGR2GRAY) > 0)
        mask_canvas = (cv.cvtColor(canvas, cv.COLOR_BGR2GRAY) > 0)
        overlap = mask_warped & mask_canvas
        new_area = mask_warped & ~mask_canvas
        
        canvas[new_area] = warped[new_area]
        canvas[overlap] = cv.addWeighted(warped, 0.5, canvas, 0.5, 0)[overlap]


    gray = cv.cvtColor(canvas, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 1, 255, cv.THRESH_BINARY)
    coords = cv.findNonZero(thresh)
    
    if coords is not None:
        x, y, w_f, h_f = cv.boundingRect(coords)
        final = canvas[y:y+h_f, x:x+w_f]
        
        display_w = 1000
        display_h = int(h_f * (display_w / w_f))
        display_img = cv.resize(final, (display_w, display_h))

        cv.imshow('Stitched Result', display_img)
        cv.imwrite('final.jpg', final) 

img_names = ['./st1.jpg', './st2.jpg', './st3.jpg', './st4.jpg']
images = prepare_images(img_names)

if images:

    cv.namedWindow('Control Panel', cv.WINDOW_AUTOSIZE)
    cv.createTrackbar('F', 'Control Panel', 1000, 2000, run_stitching)
    
    cv.namedWindow('Stitched Result', cv.WINDOW_NORMAL)
    
    run_stitching(1000)
    
    print("컨트롤 패널 창에서 트랙바를 조절하세요. 종료하려면 'q'를 누르세요.")
    while True:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cv.destroyAllWindows()