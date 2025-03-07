import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, TypeAlias

UidStr: TypeAlias = str  # Uid total


@dataclass
class Uid:
    """
    Uid data class.

    example: UID="2014741_002"
        - uid_total: 2014741_002
        * uid_global: 2014741
        * uid_local: 002
        * uid_stem: 2014741_002
        * tag: 41
    """

    uid_total: str = None

    def __post_init__(self):
        # Type check
        assert self.uid_total.count("_") == 1, self.uid_total
        assert self.uid_total.split("_")[0].isnumeric(), self.uid_total
        assert self.uid_total.split("_")[1].isnumeric(), self.uid_total
        # assert len(self.uid_total.split('_')[0]) == 7
        assert len(self.uid_total.split("_")[1]) == 3, self.uid_total
        self.uid_global = self.uid_total.split("_")[0]
        self.uid_local = self.uid_total.split("_")[1]
        self.tag = self.uid_global[-2:]
        self.uid_stem = self.uid_total

    def get_uid_dir(self, root_path: str, assert_exist: bool = False) -> str:
        "/root_path/tag/uid_total"
        output = os.path.join(root_path, self.tag, self.uid_stem)
        if assert_exist:
            assert os.path.isdir(output), output
        return output

    def get_glb_uid_path(self, root_path: str, assert_exist: bool = False) -> str:
        "/root_path/tag/uid_global/uid_total.glb"
        output = os.path.join(
            root_path, self.tag, self.uid_global, f"{self.uid_stem}.glb"
        )
        if assert_exist:
            assert os.path.isfile(output), output
        return output

    def get_json(
        self, source_dir: str, assert_exist: bool = False, key: str | None = None
    ) -> dict[str, Any]:
        """
        returns the metadata process dict.
        """
        json_path = os.path.join(
            source_dir, self.tag, self.uid_stem, "process_dict.json"
        )
        try:
            with open(json_path, "r") as f:
                X = json.load(f)
                return X if key is None else X.get(key)
        except FileNotFoundError:
            if assert_exist:
                raise Exception(f"Json {json_path} not found")
            return None


def filter_excluded_uids(
    uids_included: List[str], uids_excluded: List[str]
) -> List[str]:
    return [x for x in uids_included if x not in uids_excluded]


def intersect_uids(uid_groups: List[List[str]]) -> List[str]:
    intersection = set(uid_groups[0])
    for lst in uid_groups[1:]:
        intersection &= set(lst)
    ordered_intersection = [uid for uid in uid_groups[0] if uid in intersection]
    return ordered_intersection


def get_uids_from_txt_files(
    list_files_path: List[str], limit_per_files: int = -1, shuffle: bool = False
) -> List[str]:
    """
    Extract UIDS from text files.
    """
    output_list = []
    for list_x in list_files_path:

        with open(list_x, "r") as f:

            animated_files = f.readlines()
            current_list = [path.strip() for path in animated_files]
            current_list = [x for x in current_list if len(x) > 2]

            if shuffle:
                random.shuffle(current_list)

            if (limit_per_files != -1) and (len(current_list) > limit_per_files):
                current_list = current_list[:limit_per_files]

            output_list.extend(current_list)

    return output_list


@dataclass
class ObjvUid(Uid):
    """
    "000-0007/728277d4d33e4e5a927d2183861c32d9"

    example: UID="000-0007/728277d4d33e4e5a927d2183861c32d9"
    - uid_total: 000-0007/728277d4d33e4e5a927d2183861c32d9
    * uid_global: UNKN
    * uid_local: UNKN
    * uid_stem: 728277d4d33e4e5a927d2183861c32d9
    * tag: 000-0007

    """

    uid_total: str = None

    def __post_init__(self):
        self.tag = self.uid_total.split("/")[0]
        self.uid_stem = self.uid_total.split("/")[1]

    def get_glb_uid_path(self, root_path: str, assert_exist: bool = False) -> str:
        output = os.path.join(root_path, self.tag, f"{self.uid_stem}.glb")
        if assert_exist:
            assert os.path.isfile(output), output
        return output


def get_general_uid_from_glb_path(glb_path: str) -> Uid | ObjvUid:
    try:
        return get_uid_from_glb_path(glb_path)
    except:
        try:
            return get_objvuid_from_glb_path(glb_path)
        except:
            raise Exception(f"Invalid glb path (SSTK or OBJAVERSE): {glb_path}")


def get_uid_from_glb_path(glb_path: str) -> Uid:
    return Uid(uid_total=Path(glb_path).stem)


def get_objvuid_from_glb_path(glb_path: str) -> ObjvUid:
    uid = "/".join([Path(glb_path).parts[-2], Path(glb_path).stem])
    return ObjvUid(uid)


def get_uid_from_str(uid_str: str) -> Uid | ObjvUid | None:
    try:
        uid = Uid(uid_str)
    except:
        try:
            uid = ObjvUid(uid_str)
        except:
            uid = None
    return uid
