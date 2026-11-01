"""Screen-excess matte with authorized color-only opponent-channel cleanup."""
import cv2
import numpy as np

def color_families(c):
    """Cache the unchanged 0.3.1 color partition once per frame."""
    hsv=cv2.cvtColor(c,cv2.COLOR_RGB2HSV)
    hue=np.floor(hsv[:,:,0]/60).astype(np.int8)%6
    brightness=np.minimum((hsv[:,:,2]*3).astype(np.int8),2)
    family=hue+6*brightness
    neutral=18+brightness
    family[hsv[:,:,1]<0.2]=neutral[hsv[:,:,1]<0.2]
    return family

def foreground_candidates(c, b, seeds, lower, partial, settings, families=None):
    """Compare local foreground colors by how well each explains observed RGB.

    Separate hue/brightness families prevent a nearby white surface from hiding
    a slightly farther dark strand. Distance breaks close color-fit ties; it is
    not used as evidence that two pixels belong to the same material.
    """
    h,w=partial.shape
    result_alpha=np.zeros((h,w),np.float32)
    result_color=np.zeros_like(c)
    result_confidence=np.zeros((h,w),np.float32)
    if not np.any(seeds) or not np.any(partial):
        return result_alpha,result_color,result_confidence
    radius=settings["edge_search_radius"]
    reach=int(np.ceil(radius))
    # Any accepted chamfer-distance candidate is also in this square query.
    # This prunes impossible queries only; it does not filter the output matte.
    nearby=cv2.boxFilter(seeds.astype(np.uint8),cv2.CV_32S,
        (2*reach+1,2*reach+1),normalize=False,borderType=cv2.BORDER_CONSTANT)>0
    y,x=np.nonzero(partial & nearby)
    if not len(y):
        return result_alpha,result_color,result_confidence
    halo=reach+2
    top=max(0,int(y.min())-halo);bottom=min(h,int(y.max())+halo+1)
    left=max(0,int(x.min())-halo);right=min(w,int(x.max())+halo+1)
    region=np.s_[top:bottom,left:right]
    local_c=c[region]
    local_seeds=seeds[region]
    if families is None:families=color_families(c)
    local_family=families[region]
    yy,xx=y-top,x-left
    observed=c[y,x]
    delta=observed-b
    lower_values=lower[y,x]
    best_score=np.full(len(y),np.inf,np.float32)
    best_error=np.full(len(y),np.inf,np.float32)
    best_alpha=np.zeros(len(y),np.float32)
    best_color=np.zeros((len(y),3),np.float32)
    for group in np.unique(local_family[local_seeds]):
        selected=local_seeds & (local_family==group)
        distances,labels = cv2.distanceTransformWithLabels(
            (~selected).astype(np.uint8),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
        palette = np.zeros((int(labels.max())+1,3),np.float32)
        palette[labels[selected]] = local_c[selected]
        color = palette[labels[yy,xx]]
        distance=distances[yy,xx]
        direction = color-b
        denominator = np.sum(direction*direction,axis=1)
        a = np.clip(np.sum(delta*direction,axis=1)/np.maximum(denominator,1e-8),0,1)
        a = np.maximum(a,lower_values)
        residual = observed-((1-a[:,None])*b+a[:,None]*color)
        error = np.sqrt(np.mean(residual*residual,axis=1))
        score = error*error+(settings["edge_spatial_weight"]*distance)**2
        choose = (distance<=radius) & (denominator>0.02)
        choose &= (error<settings["edge_fit_tolerance"]) & (score<best_score)
        best_score[choose] = score[choose]
        best_error[choose] = error[choose]
        best_alpha[choose] = a[choose]
        best_color[choose] = color[choose]
    confidence = np.clip(1-best_error/settings["edge_fit_tolerance"],0,1)
    result_alpha[y,x]=best_alpha
    result_color[y,x]=best_color
    result_confidence[y,x]=confidence
    return result_alpha,result_color,result_confidence

def material_protection(foreground,known,targets,radius,tolerance):
    """A bounded color match to stable material interiors, not a hue classifier."""
    protected=np.zeros(targets.shape,bool)
    if radius<=0 or not np.any(known) or not np.any(targets):return protected
    reach=int(np.ceil(radius));halo=reach+2
    nearby=cv2.boxFilter(known.astype(np.uint8),cv2.CV_32S,(2*reach+1,2*reach+1),
        normalize=False,borderType=cv2.BORDER_CONSTANT)>0
    y,x=np.nonzero(targets & nearby)
    if not len(y):return protected
    h,w=targets.shape
    top=max(0,int(y.min())-halo);bottom=min(h,int(y.max())+halo+1)
    left=max(0,int(x.min())-halo);right=min(w,int(x.max())+halo+1)
    region=np.s_[top:bottom,left:right];selected=known[region]
    distance,labels=cv2.distanceTransformWithLabels((~selected).astype(np.uint8),
        cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    palette=np.zeros((int(labels.max())+1,3),np.float32)
    palette[labels[selected]]=foreground[region][selected]
    yy,xx=y-top,x-left
    reference=palette[labels[yy,xx]]
    close=(distance[yy,xx]<=radius) & (np.max(np.abs(foreground[y,x]-reference),axis=1)<=tolerance)
    protected[y[close],x[close]]=True
    return protected

def despill_colors(foreground,alpha,k,stable,locked,settings):
    """RGB-only adaptation of the authorized MIT 0.2 opponent-bound stage.

    The 0.2 alpha, haze removal, reference erosion and pipeline are not inherited.
    Material-interior matching is a new conservative guard with explicit limits.
    """
    strength=settings["edge_despill_strength"]
    if strength==0:return foreground,0,0
    alternatives=[i for i in range(3) if i!=k]
    balance=settings["edge_despill_balance"]
    if balance is None:balance=0.0 if k==2 else 0.5
    width=settings["edge_despill_width"]
    distance=cv2.distanceTransform((alpha>=.995).astype(np.uint8),cv2.DIST_L2,3)
    fringe=(alpha>.025) & ((alpha<.995)|(distance<=width)) & ~locked
    low=foreground[:,:,alternatives].min(axis=2)
    high=foreground[:,:,alternatives].max(axis=2)
    ceiling=low+balance*(high-low)+settings["spill_allowance"]
    spill=np.maximum(foreground[:,:,k]-ceiling,0)
    targets=fringe & (spill>0)
    # Neither input hue nor estimated alpha=1 alone authenticates a material.
    # Require a stable interior beyond the contour and an actual RGB match.
    known=(alpha>=.995) & (distance>width+1) & stable & (spill>0)
    material=material_protection(foreground,known,targets,
        settings["material_protection_radius"],settings["material_protection_tolerance"])
    amount=spill*strength*(fringe & ~material)
    foreground[:,:,k]-=amount
    return foreground,int((amount>.5/255).sum()),int(material.sum())

def extract(rgb, screen, roi, settings, core=None, preserve=None):
    c = rgb.astype(np.float32) / 255.0
    h, w = c.shape[:2]
    left, top, right, bottom = roi
    if right > w or bottom > h:
        raise ValueError("background_roi outside image")
    patch = c[top:bottom, left:right]
    b = np.median(patch.reshape(-1, 3), axis=0)
    if np.max(np.abs(patch - b)) > settings["roi_max_deviation"]:
        raise ValueError("background_roi is not sufficiently uniform")
    k = 1 if screen == "green" else 2
    others = [i for i in range(3) if i != k]
    dominance = float(b[k] - max(b[others]))
    if dominance < 0.15:
        raise ValueError("sample is not the selected dominant screen color")
    distance = np.max(np.abs(c - b), axis=2)
    excess = c[:, :, k] - np.max(c[:, :, others], axis=2)
    alpha = np.clip(1.0 - np.maximum(excess, 0) / dominance, 0, 1)
    # Codec/sample uncertainty must be allowed before applying gamut constraints.
    # An exact bound at a nearly saturated screen channel turns a one-code-value
    # overshoot into an opaque foreground seed, so it is intentionally relaxed.
    uncertainty = settings["background_tolerance"]
    lower = np.maximum((b[k]-c[:,:,k]-uncertainty) / max(float(b[k]),1e-6),
                       np.max((c[:,:,others]-b[others]-uncertainty) /
                              np.maximum(1-b[others],1e-6),axis=2))
    alpha = np.maximum(alpha, np.clip(lower, 0, 1))
    background = distance <= settings["background_tolerance"]
    alpha[background] = 0
    rejected = accepted = 0
    protected = np.zeros((h, w), bool)
    if core is not None:
        requested = core >= settings["core_threshold"]
        protected = requested & (distance > settings["core_background_guard"])
        accepted, rejected = int(protected.sum()), int((requested & ~protected).sum())
        alpha[protected] = 1
    # Initial screen excess can saturate to alpha=1 inside a colored coverage
    # ramp. Such a changing RGB sample is not a trustworthy opaque color seed.
    # This is a color-statistics test; it never filters/moves the output matte.
    mean = cv2.boxFilter(c,-1,(3,3),normalize=True,borderType=cv2.BORDER_REFLECT)
    squared = cv2.boxFilter(c*c,-1,(3,3),normalize=True,borderType=cv2.BORDER_REFLECT)
    variation = np.sqrt(np.maximum(squared-mean*mean,0)).max(axis=2)
    stable = variation <= settings["seed_color_variation"]
    opaque_estimate = (alpha >= 0.995) & ~background
    seeds = opaque_estimate & (stable | protected)
    radius = settings["edge_search_radius"]
    nearest = None
    confidence = np.zeros((h,w),np.float32)
    if radius > 0 and np.any(opaque_estimate):
        families=color_families(c)
        partial = (alpha>0) & (alpha<0.995) & ~protected
        candidate,nearest,confidence = foreground_candidates(c,b,seeds,lower,partial,settings,families)
        # A smooth-color requirement can leave textured hair/skin/metal without
        # any compatible reference. Fall back to the same multi-family fit on
        # textured estimates only where stable references provide no valid fit.
        missing = partial & (confidence<=0)
        if np.any(missing) and np.any(opaque_estimate & ~seeds):
            fallback,color,trust = foreground_candidates(c,b,opaque_estimate,lower,missing,settings,families)
            choose = missing & (trust>0)
            candidate[choose] = fallback[choose]
            nearest[choose] = color[choose]
            confidence[choose] = trust[choose]
        # Fit confidence decides whether a color model is compatible. Mixing a
        # valid projected coverage back toward the screen-excess estimate can
        # artificially raise alpha and recreate green/olive fringes.
        fitted = confidence>0
        alpha[fitted] = candidate[fitted]
    alpha[protected] = 1
    alpha[alpha <= settings["alpha_floor"]] = 0
    foreground = np.clip((c - (1-alpha[:, :, None])*b) / np.maximum(alpha[:, :, None], 1e-6), 0, 1)
    if nearest is not None:
        # A color prior is allowed to act only to the extent it explains C as a
        # composite. An incompatible nearby white hair cannot wash out a dark
        # string simply because its seed is the nearest opaque pixel.
        brightness_delta = np.clip(np.mean(foreground-nearest,axis=2,keepdims=True),-0.04,0.04)
        prior = np.clip(nearest+brightness_delta,0,1)
        strength = confidence*(1-alpha**4)
        foreground += strength[:,:,None]*(prior-foreground)
    # A soft pixel dominated by the key channel is ambiguous, especially when
    # codec chroma ringing violates the simple composite. Remove only its excess
    # key-channel chroma. Authenticated core/preservation pixels bypass this.
    soft_screen = (alpha < 0.995) & (excess > 0) & ~protected
    limit = np.max(foreground[:,:,others],axis=2)
    foreground[:,:,k][soft_screen] = np.minimum(foreground[:,:,k],limit)[soft_screen]
    foreground,despilled,material_pixels=despill_colors(foreground,alpha,k,stable,protected,settings)
    rgba = np.concatenate((np.rint(foreground*255).astype(np.uint8),
                           np.rint(alpha[:, :, None]*255).astype(np.uint8)), axis=2)
    rgba[rgba[:, :, 3] == 0, :3] = 0
    rgba[protected, :3] = rgb[protected]
    rgba[protected, 3] = 255
    if preserve is not None:
        selected = preserve[:, :, 3] > 0
        rgba[selected] = preserve[selected]
    return rgba, {"background_rgb": [int(x) for x in np.rint(b*255)],
                  "core_accepted_pixels": accepted, "core_rejected_background_pixels": rejected,
                  "edge_despill_pixels":despilled,"material_protected_pixels":material_pixels}
