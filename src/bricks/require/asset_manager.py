import threading

from bricks.require import Bundle, Asset

possible_assets = Asset.possible_assets


class AssetManager:
    """
    Specify assets necessary to render a given set of components.
    """

    _manager_state = threading.local()
    _manager_state.current_manager = None

    @property
    def current_manager(self):
        try:
            return self._manager_state.current_manager
        except AttributeError:
            return None

    @property
    def assets(self):
        if self._assets is None:
            self._assets = self.resolve_dependencies()
        return self._assets

    @classmethod
    def get_current_manager(cls):
        """
        Return the current thread-local AssetManager or None if no manager is
        defined.
        """

        return getattr(AssetManager._manager_state, 'current_manager', None)

    def __init__(self):
        self._required = []
        self._assets = None
        self._registered_classes = set()

    def resolve_dependencies(self):
        """
        Return a list with the minimal dependencies required to fulfill all
        asset requirements.
        """

        # Obtain all assets that may fulfill requirements. We need to linearize
        # bundles bundles and save them in the list of dependencies
        dependencies = list(self._required)
        possible = {name: possible_assets(name) for name in self._required}
        for name in list(dependencies):
            L = possible[name]
            non_bundle = [x for x in L if not isinstance(x, Bundle)]
            if non_bundle:
                possible[name] = non_bundle
            elif len(L) == 1:
                bundle = L[0]
                idx = dependencies.index(name)
                del dependencies[idx]
                for dependency in bundle:
                    if dependency not in possible:
                        possible[dependency] = possible_assets(dependency)
                        dependencies.insert(idx, dependency)
                        idx += 1
                del possible[name]
            else:
                raise ValueError('more than 1 bundle for %r' % name)

        # Remove all elements from the list of possible elements when we single
        # out one asset for each dependency.
        assets = {}
        possible_size = len(possible)
        while possible:
            new = {k: L[0] for k, L in possible.items() if len(L) == 1}
            assets.update(new)
            possible = {k: L for k, L in possible.items() if k not in new}

            # Remove all fulfilled dependencies
            for asset in set(assets.values()):
                for provided in asset.provides:
                    if provided in possible:
                        del possible[provided]
                        assets[provided] = asset

            # Stop if possible assets do not shrink in the interaction
            if len(possible) == possible_size:
                raise RuntimeError(
                    'could not determine a single value for assets: %s'
                    % possible
                )
            possible_size = len(possible)

        # Re-order assets in declaration order
        asset_list = []
        for name in dependencies:
            asset = assets[name]
            if asset not in asset_list:
                asset_list.append(asset)

        # Load dependencies: we move assets from tail to head and include
        # dependencies on demand
        def tail_dep(dep, push_back=False):
            result = None
            idx = None
            for idx, x in enumerate(tail):
                if x.provide(dep):
                    result = x
                    break

            if push_back:
                if idx is not None:
                    del tail[idx]
                tail.append(push_back)
                if result:
                    tail.append(result)

            return result

        def head_dep(dep):
            for x in head:
                if x.provide(dep):
                    return x

        def get_dependency(name, new):
            dep = possible_assets(name)[-1]

            if not isinstance(dep, Bundle):
                if not dep.requires:
                    head.append(dep)
                    return None
                else:
                    return dep
            else:
                for dep in dep:
                    if head_dep(dep):
                        continue
                    elif tail_dep(dep, push_back=new):
                        return tail.pop()
                    else:
                        dep = get_dependency(dep, new)
                        if dep:
                            return dep

        head, tail = [], asset_list[::-1]
        while tail:
            new = tail.pop()
            if not new.requires:
                head.append(new)
                continue

            for name in new.requires:
                if head_dep(name):
                    continue
                elif tail_dep(name, push_back=new):
                    break
                else:
                    required_asset = get_dependency(name, new)
                    if required_asset is not None:
                        tail.append(required_asset)
                        break
            else:
                tail.pop()
                head.append(new)

        return head

    def require(self, *assets):
        """
        Requires the given asset
        """

        for asset in assets:
            if asset not in self._required:
                self._required.append(asset)

    def register_class(self, cls):
        try:
            getter = cls.required_class_assets
        except AttributeError:
            return

        self.require(*getter())

    def register_instance(self, obj):
        """
        Register a component instance and inspect all of its requirements.
        """

        cls = type(obj)
        if cls not in self._registered_classes:
            self.register_class(cls)
            self._registered_classes.add(cls)

        # Check requirements
        try:
            getter = obj.required_assets
        except AttributeError:
            pass
        else:
            for requirement in getter():
                if requirement not in self._required:
                    self._required.append(requirement)

    def render_js(self):
        return self.render('js')

    def render_js_head(self):
        return self.render('js_head')

    def render_js_foot(self):
        return self.render('js_head')

    def render_js_on_load(self):
        return self.render('js_on_load')

    def render_css(self):
        return self.render('css')

    def render(self, name):
        lines = []
        for asset in self.assets:
            data = asset.render(name)
            if data:
                lines.append(data)
        return '\n'.join(lines)

    def render_head(self):
        L = [
            self.render_css(),
            self.render_js_head(),
        ]
        return '\n'.join([x for x in L if x])

    def render_foot(self):
        L = [
            self.render_js_foot(),
            self.render_js_on_load(),
        ]
        return '\n'.join([x for x in L if x])

    # Global state
    def capture(self):
        if self._manager_state.current_manager is not self:
            self._manager_state.current_manager = self
        else:
            raise RuntimeError('different manager already capturing assets')

    def release(self):
        if self._manager_state.current_manager is self:
            self._manager_state.current_manager = None
        else:
            raise RuntimeError('not capturing assets')
