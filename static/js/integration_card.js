const IntegrationCard = {
    props: ['id', 'name', 'section', 'settings', 'is_default', 'description', 'task_id'],
    delimiters: ['[[', ']]'],
    computed: {
        reflected_component() {
            const obj = this.$root.registered_components[this.name]
            !obj && console.warn('No reflected component found for', this.name)
            obj && !obj.handleEdit && console.warn('.handleEdit method not implemented for for', this.name)
            obj && !obj.handleDelete && console.warn('.handleDelete method not implemented for for', this.name)
            return obj
        },
        display_name() {
            return this.reflected_component?.display_name || this.name
        },
        logo() {
            return this.reflected_component?.logo_src
        }
    },
    methods: {
        handle_edit() {
            this.reflected_component.handleEdit(this.$props)
        },
        handle_delete() {
            this.reflected_component.handleDelete(this.id)
        },
    },
    template: `
<div class="card card-row-1 mx-3 integration_card p-2 flex-row">
    <div class="d-flex align-items-center justify-content-center integration_icon_container">
        <div><img class="integration_icon" :src="logo" /></div>
    </div>
    <div class="d-flex flex-column justify-content-center flex-grow-1">
        <div>
            <h3>
                [[ display_name ]]
            </h3>
        </div>
        <div>
            <h13 class="integration_description">[[ description ]]</h13>
        </div>
    </div>
    <div class="d-flex flex-column justify-content-between">
        <div class="dropdown dropleft dropdown_action text-right">
            <button class="btn dropdown-toggle btn-action"
                    role="button"
                    data-toggle="dropdown"
                    aria-expanded="false">
                <i class="fas fa-ellipsis-h"></i>
            </button>

            <ul class="dropdown-menu">
                <li class="dropdown-item" @click="handle_edit">
                    <i class="fas fa-cog mr-2"></i>Edit
                </li>
                <li class="dropdown-item" @click="handle_delete">
                    <i class="fas fa-trash-alt mr-2"></i>Delete
                </li>
            </ul>
        </div>
        <div class="text-right mb-3" style="font-size: small" v-if="is_default">
            <h13 class="badge badge-pill badge-primary text-uppercase">default</h13>
        </div>
    </div>
</div>
`
}
register_component('IntegrationCard', IntegrationCard)