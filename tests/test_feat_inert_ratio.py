import h5py
import numpy as np
import pytest

import dclab
from dclab import new_dataset
from dclab.features import inert_ratio as ir

from helper_methods import retrieve_data


@pytest.mark.filterwarnings('ignore::dclab.rtdc_dataset.'
                            + 'feat_anc_core.ancillary_feature.'
                            + 'BadFeatureSizeWarning')
def test_af_inert_ratio_cvx():
    pytest.importorskip("nptdms")
    # Brightness of the image
    ds = dclab.new_dataset(retrieve_data("fmt-tdms_fl-image-bright_2017.zip"))
    # This is something low-level and should not be done in a script.
    # Remove the brightness columns from RTDCBase to force computation with
    # the image and contour columns.
    real_ir = ds._events.pop("inert_ratio_cvx")
    # This will cause a zero-padding warning:
    comp_ir = ds["inert_ratio_cvx"]
    idcompare = ~np.isnan(comp_ir)
    # ignore first event (no image data)
    idcompare[0] = False
    assert np.allclose(real_ir[idcompare], comp_ir[idcompare])


@pytest.mark.filterwarnings('ignore::dclab.rtdc_dataset.'
                            + 'feat_anc_core.ancillary_feature.'
                            + 'BadFeatureSizeWarning')
def test_af_inert_ratio_prnc():
    pytest.importorskip("nptdms")
    # Brightness of the image
    ds = dclab.new_dataset(retrieve_data("fmt-tdms_fl-image-bright_2017.zip"))
    # This will cause a zero-padding warning:
    prnc = ds["inert_ratio_prnc"]
    raw = ds["inert_ratio_raw"]
    idcompare = ~np.isnan(prnc)
    # ignore first event (no image data)
    idcompare[0] = False
    diff = (prnc - raw)[idcompare]
    # only compare the first valid event which seems to be quite close
    assert np.allclose(diff[0], 0, atol=1.2e-3, rtol=0)


@pytest.mark.filterwarnings(
    "ignore::dclab.rtdc_dataset.config.WrongConfigurationTypeWarning")
@pytest.mark.filterwarnings(
    'ignore::dclab.rtdc_dataset.config.UnknownConfigurationKeyWarning')
@pytest.mark.parametrize("file", [
    "fmt-hdf5_fl_2017.zip",
    "fmt-hdf5_mask-contour_2018.zip",
    "fmt-hdf5_image-bg_2020.zip",
    "fmt-hdf5_polygon_gate_2021.zip",
    "fmt-hdf5_fl_wide-channel_2023.zip",
    ])
def test_af_inert_ratio_prnc_greater_than_one_issue_212(file):
    ds = new_dataset(retrieve_data(file))
    prnc = ds["inert_ratio_prnc"]
    assert np.all(prnc >= 1)


@pytest.mark.filterwarnings('ignore::dclab.rtdc_dataset.'
                            + 'feat_anc_core.ancillary_feature.'
                            + 'BadFeatureSizeWarning')
def test_af_inert_ratio_raw():
    pytest.importorskip("nptdms")
    # Brightness of the image
    ds = dclab.new_dataset(retrieve_data("fmt-tdms_fl-image-bright_2017.zip"))
    # This is something low-level and should not be done in a script.
    # Remove the brightness columns from RTDCBase to force computation with
    # the image and contour columns.
    real_ir = ds._events.pop("inert_ratio_raw")
    # This will cause a zero-padding warning:
    comp_ir = ds["inert_ratio_raw"]
    idcompare = ~np.isnan(comp_ir)
    # ignore first event (no image data)
    idcompare[0] = False
    assert np.allclose(real_ir[idcompare], comp_ir[idcompare])


@pytest.mark.filterwarnings(
    "ignore::dclab.rtdc_dataset.config.WrongConfigurationTypeWarning")
def test_inert_ratio_raw():
    ds = new_dataset(retrieve_data("fmt-hdf5_mask-contour_2018.zip"))

    raw = ir.get_inert_ratio_raw(cont=ds["contour"])
    ref = np.array([4.25854232,  1.22342663,  4.64971179,  1.70914857,
                    3.62797492, 1.51502192,  2.74757573,  1.79841136])
    assert np.allclose(ref, raw, rtol=0, atol=5e-9)


def test_inert_ratio_raw_correct_issue_224():
    path = retrieve_data("fmt-hdf5_wide-channel_2023.zip")

    # make the file look like it has been created with an old Shape-In version
    with h5py.File(path, "a") as h5:
        h5["events/inert_ratio_cvx"][:] = 1
        assert np.allclose(h5["events/inert_ratio_cvx"][:], 1)
        h5.attrs["setup:software version"] = "ShapeIn 2.0.4 | dclab 0.49.0"

    ds = dclab.new_dataset(path)
    assert "inert_ratio_cvx" in ds.features_loaded
    assert np.allclose(ds["inert_ratio_cvx"], 1)


def test_inert_ratio_raw_with_integer_precision_issue_223():
    """Test computation of inert_ratio_raw

    On Windows, we had the problem that due to the default integer
    not being int64, the inertia ratio was not computed correctly.
    """
    path = retrieve_data("fmt-hdf5_wide-channel_2023.zip")

    # make the file look like it has been created with an old Shape-In version
    with h5py.File(path, "a") as h5:
        inert_ratio_raw = h5["events/inert_ratio_raw"][:]
        del h5["events/inert_ratio_raw"]

    ds = dclab.new_dataset(path)
    assert "inert_ratio_raw" not in ds.features_loaded
    assert np.allclose(inert_ratio_raw,
                       ds["inert_ratio_raw"],
                       atol=0,
                       rtol=1e-5,
                       equal_nan=False,  # sic!
                       )
    assert not np.sum(np.isnan(ds["inert_ratio_raw"]))


def test_inert_ratio_raw_with_old_dclab_issue_224():
    path = retrieve_data("fmt-hdf5_wide-channel_2023.zip")

    # make the file look like it has been created with an old Shape-In version
    with h5py.File(path, "a") as h5:
        h5.attrs["setup:software version"] = "ShapeIn 2.0.4 | dclab 0.48.0"

    ds = dclab.new_dataset(path)
    assert "inert_ratio_cvx" not in ds.features_loaded


def test_inert_ratio_raw_with_old_shapein_issue_224():
    path = retrieve_data("fmt-hdf5_wide-channel_2023.zip")

    # make the file look like it has been created with an old Shape-In version
    with h5py.File(path, "a") as h5:
        h5["events/inert_ratio_cvx"][:] = 1
        assert np.allclose(h5["events/inert_ratio_cvx"][:], 1)
        h5.attrs["setup:software version"] = "ShapeIn 2.0.4"

    ds = dclab.new_dataset(path)
    assert "inert_ratio_cvx" in ds.features_loaded


@pytest.mark.parametrize("si_string", ["ShapeIn 2.0.5", "2.3.1"])
def test_inert_ratio_with_new_shapein_issue_224(si_string):
    path = retrieve_data("fmt-hdf5_wide-channel_2023.zip")

    # make the file look like it has been created with an old Shape-In version
    with h5py.File(path, "a") as h5:
        h5["events/inert_ratio_cvx"][:] = 1
        assert np.allclose(h5["events/inert_ratio_cvx"][:], 1)
        h5.attrs["setup:software version"] = si_string + " | dclab 0.47.2"
        # Create a Shape-In acquisition log so that it is not considered a
        # defective feature.
        h5["logs/shapein-acquisition"] = ["test"]

    ds = dclab.new_dataset(path)
    assert "inert_ratio_cvx" in ds.features_loaded


def test_inert_ratio_prnc():
    """Test equivalence of inert_ratio_raw and inert_ratio_prnc"""
    t = np.linspace(0, 2*np.pi, 300)

    x1 = 1.7 * np.cos(t)
    y1 = 1.1 * np.sin(t)
    c1 = np.dstack((x1, y1))[0]
    raw = ir.get_inert_ratio_raw(c1)

    phi = np.arctan2(y1, x1)
    rho = np.sqrt(x1**2 + y1**2)

    for theta in np.linspace(0.1, 2*np.pi, 14):  # arbitrary rotation
        for pos_x in np.linspace(-5, 20, 8):  # arbitrary x shift
            for pos_y in np.linspace(-4.6, 17, 4):  # arbitrary y shift
                x2 = rho * np.cos(phi + theta) + pos_x
                y2 = rho * np.sin(phi + theta) + pos_y

                c2 = np.dstack((x2, y2))[0]
                prnc = ir.get_inert_ratio_prnc(c2)

                assert np.allclose(raw, prnc, rtol=0, atol=1e-7)


def test_inert_ratio_prnc_simple_1():
    c = np.array([[0, 0],
                  [0, 1],
                  [0, 2],
                  [1, 2],
                  [2, 2],
                  [3, 2],
                  [3, 1],
                  [3, 0],
                  [2, 0],
                  [1, 0],
                  [0, 0]])
    raw = ir.get_inert_ratio_raw(c)
    prnc = ir.get_inert_ratio_prnc(c)
    tilt = ir.get_tilt(c)
    assert np.allclose(raw, 1.5)
    assert np.allclose(prnc, 1.5)
    assert np.allclose(tilt, 0)


def test_inert_ratio_prnc_simple_2():
    c = np.array([[0, 0],
                  [1, 1],
                  [2, 2],
                  [3, 3],
                  [4, 2],
                  [5, 1],
                  [4, 0],
                  [3, -1],
                  [2, -2],
                  [1, -1],
                  [0, 0]])
    raw = ir.get_inert_ratio_raw(c)
    prnc = ir.get_inert_ratio_prnc(c)
    tilt = ir.get_tilt(c)
    assert np.allclose(raw, 1)
    assert np.allclose(prnc, 1.5)
    assert np.allclose(tilt, np.pi/4)


def test_tilt():
    t = np.linspace(0, 2*np.pi, 300)

    x1 = 1.7 * np.cos(t)
    y1 = 1.1 * np.sin(t)

    phi = np.arctan2(y1, x1)
    rho = np.sqrt(x1**2 + y1**2)

    for theta in np.linspace(-.3, 2.2*np.pi, 32):  # arbitrary rotation
        x2 = rho * np.cos(phi + theta)
        y2 = rho * np.sin(phi + theta)

        c2 = np.dstack((x2, y2))[0]
        tilt = ir.get_tilt(c2)

        th = np.mod(theta, np.pi)
        if th > np.pi/2:
            th -= np.pi
        th = np.abs(th)
        assert np.allclose(tilt, th)
